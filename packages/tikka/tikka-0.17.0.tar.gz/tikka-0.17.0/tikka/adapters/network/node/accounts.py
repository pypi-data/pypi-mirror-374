# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from scalecodec import ScaleBytes

from tikka.domains.entities.account import AccountBalance
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.node.accounts import (
    NodeAccountsException,
    NodeAccountsInterface,
)
from tikka.libs.keypair import Keypair

if TYPE_CHECKING:
    from tikka.adapters.network.node.node import NetworkNode


class NodeAccounts(NodeAccountsInterface):
    """
    NodeAccounts class
    """

    def __init__(self, node: "NetworkNode") -> None:
        """
        Use NetworkNodeInterface to request/send smiths information

        :param node: NetworkNodeInterface instance
        :return:
        """
        self.node = node

    def get_balance(self, address: str) -> Optional[AccountBalance]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAccountsInterface.get_balance.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAccountsException(NetworkConnectionError())

        # system.account: FrameSystemAccountInfo
        # {
        #   nonce: 1
        #   consumers: 0
        #   providers: 1
        #   sufficients: 0
        #   data: {
        #     randomId: 0x18a4d...
        #     free: 9,799
        #     reserved: 0
        #     feeFrozen: 0
        #   }
        # }
        balance = None

        # {
        #   /// full balance owned
        #   total: number,
        #
        #   /// full available balance (include unclaimed UDs, but without existence deposit and reserved funds)
        #   transferable: number,
        #
        #   /// Unclaimed UDs
        #   unclaim_uds: number
        # }
        # fixme: should use a runtime_call() in substrate_client, see https://forum.duniter.org/t/proposition-pour-obtenir-facilement-le-solde-dun-compte-sans-indexeur/13154/5
        public_key = Keypair(ss58_address=address).public_key.hex()
        try:
            result = self.node.connection.client.rpc_request(
                "state_call", ["UniversalDividendApi_account_balances", public_key]
            )
        except Exception as exception:
            logging.exception(exception)
            return self.get_balance_obsolete(address)
        else:
            if result is not None:
                result_obj = (
                    self.node.connection.client.runtime_config.create_scale_object(
                        "(u64,u64,u64)"
                    )
                )
                result_obj.decode(ScaleBytes(result["result"]), check_remaining=True)
                balance = AccountBalance(
                    # total balance
                    result_obj.value[0],
                    # balance without existential deposit, reserved funds and unclaimed UDs
                    result_obj.value[1] - result_obj.value[2],
                    # existential deposit + reserved funds
                    result_obj.value[0] - result_obj.value[1],
                )

        return balance

    def get_balance_obsolete(self, address: str) -> Optional[AccountBalance]:
        """
        Return AccountBalance by calculating manually the unclaimed UDs

        :param address: Account address
        :return:
        """
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAccountsException(NetworkConnectionError())

        # compatibility with duniter 900 (gdev)
        # todo: remove as soon as gdev is upgraded with Duniter 0.10.x
        try:
            result = self.node.connection.client.query("System", "Account", [address])
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        if result is not None:
            balance = AccountBalance(
                result["data"]["free"] + result["data"]["reserved"],
                result["data"]["free"],
                result["data"]["reserved"],
            )
        else:
            return None

        try:
            result = self.node.connection.client.get_constant(
                "Balances", "ExistentialDeposit"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        balance.reserved += result

        # get unclaimed UDs amount to calculate total balance
        try:
            identity = self.node.identities.get_identity(address)
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        if identity is not None:
            try:
                result = self.node.connection.client.query(
                    "UniversalDividend", "CurrentUdIndex"
                )
            except Exception as exception:
                logging.exception(exception)
                raise NodeAccountsException(exception)

            current_index = result
            if current_index is not None:
                try:
                    result = self.node.connection.client.query(
                        "UniversalDividend", "PastReevals"
                    )
                except Exception as exception:
                    logging.exception(exception)
                    raise NodeAccountsException(exception)

                if result is not None:
                    unclaimed_uds_balance = 0
                    index = current_index
                    for reeval_index, reeval_value in reversed(result):
                        if reeval_index <= identity.first_eligible_ud:
                            count = index - identity.first_eligible_ud
                            unclaimed_uds_balance += count * reeval_value
                            break
                        else:
                            count = index - reeval_index
                            unclaimed_uds_balance += count * reeval_value
                            index = reeval_index
                    balance.total += unclaimed_uds_balance

        return balance

    def get_balances(self, addresses: List[str]) -> Dict[str, Optional[AccountBalance]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAccountsInterface.get_balances.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAccountsException(NetworkConnectionError())

        balances: Dict[str, Optional[AccountBalance]] = {}
        for address in addresses:

            balance = None

            # fixme: should use a runtime_call() in substrate_client, see https://forum.duniter.org/t/proposition-pour-obtenir-facilement-le-solde-dun-compte-sans-indexeur/13154/5
            public_key = Keypair(ss58_address=address).public_key.hex()
            try:
                result = self.node.connection.client.rpc_request(
                    "state_call", ["UniversalDividendApi_account_balances", public_key]
                )
            except Exception as exception:
                logging.exception(exception)
                return self.get_balances_obsolete(addresses)
            else:
                if result is not None:
                    result_obj = (
                        self.node.connection.client.runtime_config.create_scale_object(
                            "(u64,u64,u64)"
                        )
                    )
                    result_obj.decode(
                        ScaleBytes(result["result"]), check_remaining=True
                    )
                    balance = AccountBalance(
                        # total balance
                        result_obj.value[0],
                        # balance without existential deposit, reserved funds and unclaimed UDs
                        result_obj.value[1] - result_obj.value[2],
                        # existential deposit + reserved funds
                        result_obj.value[0] - result_obj.value[1],
                    )
                    balances[address] = balance
                else:
                    balances[address] = None

        return balances

    def get_balances_obsolete(
        self, addresses: List[str]
    ) -> Dict[str, Optional[AccountBalance]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAccountsInterface.get_balances.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAccountsException(NetworkConnectionError())

        try:
            result = self.node.connection.client.query(
                "UniversalDividend", "CurrentUdIndex"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        current_ud_index = result

        try:
            reevals_result = self.node.connection.client.query(
                "UniversalDividend", "PastReevals"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        if reevals_result is None:
            raise NodeAccountsException(
                "get_balances_obsolete UniversalDividend.PastReevals is None"
            )

        try:
            identities = self.node.identities.get_identities(addresses)
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        try:
            existential_deposit_result = self.node.connection.client.get_constant(
                "Balances", "ExistentialDeposit"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        storage_functions = []
        for address in addresses:
            storage_functions.append(("System", "Account", [address]))

        try:
            multi_result = self.node.connection.client.query_multi(storage_functions)
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        balances: Dict[str, Optional[AccountBalance]] = {}
        for index, value_obj in enumerate(multi_result):
            if value_obj is None:
                balances[addresses[index]] = None
            else:
                balances[addresses[index]] = AccountBalance(
                    value_obj["data"]["free"] + value_obj["data"]["reserved"],
                    value_obj["data"]["free"],
                    value_obj["data"]["reserved"],
                )
                if existential_deposit_result is not None:
                    balances[addresses[index]].reserved += existential_deposit_result  # type: ignore

                if (
                    identities[addresses[index]] is not None
                    and current_ud_index is not None
                ):
                    unclaimed_uds_balance = 0
                    current_ud_index_ = current_ud_index
                    for reeval_index, reeval_value in reversed(reevals_result):
                        if (
                            reeval_index
                            <= identities[addresses[index]].first_eligible_ud  # type: ignore
                        ):
                            count = (
                                current_ud_index_
                                - identities[addresses[index]].first_eligible_ud  # type: ignore
                            )
                            unclaimed_uds_balance += count * reeval_value
                            break
                        else:
                            count = current_ud_index_ - reeval_index
                            unclaimed_uds_balance += count * reeval_value
                            current_ud_index_ = reeval_index
                    balances[addresses[index]].total += unclaimed_uds_balance  # type: ignore

        return balances
