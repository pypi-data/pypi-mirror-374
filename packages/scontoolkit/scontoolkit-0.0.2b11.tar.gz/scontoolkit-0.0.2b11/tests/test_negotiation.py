#
# import unittest
# from typing import  Any
#
# from src.scontoolkit.interfaces.slg.test import INegotiator
# from src.scontoolkit.services.negotiation.bidding import BehaviorMatchingFSJStrategy
# from src.scontoolkit.services.negotiation.odrl_adapter import ODRLAdapter
# from src.scontoolkit.services.negotiation.acceptance import ProbabilisticThreshold
# from src.scontoolkit.services.negotiation.opponent import FrequencyOpponentModel
# from src.scontoolkit.services.negotiation.utility import UtilityModel
# from src.scontoolkit.services.negotiation.helpers import build_weights, _ideals_worsts
#
# provider = {
#   "@context": "http://www.w3.org/ns/odrl.jsonld",
#   "type": "Offer",
#   "uid": "urn:example:provider-offer",
#   "assigner": "did:example:provider-001",
#   "assignee": [
#     "did:example:consumer-001"
#   ],
#   "target": [
#     "urn:asset:demo-1"
#   ],
#   "permission": [
#     {
#       "action": "use",
#       "constraint": [
#         {
#           "leftOperand": "odrl:purpose",
#           "operator": "odrl:isAnyOf",
#           "rightOperand": [
#             "research",
#             "analytics"
#           ]
#         },
#         {
#           "leftOperand": "odrl:payAmount",
#           "operator": "odrl:gteq",
#           "rightOperand": 8000
#         },
#         {
#           "leftOperand": "odrl:unit",
#           "operator": "odrl:eq",
#           "rightOperand": "USD"
#         },
#         {
#           "leftOperand": "odrl:dateTime",
#           "operator": "odrl:gteq",
#           "rightOperand": "2025-09-03T12:00:00Z"
#         },
#         {
#           "leftOperand": "odrl:dateTime",
#           "operator": "odrl:lteq",
#           "rightOperand": "2026-09-03T12:00:00Z"
#         }
#       ]
#     }
#   ],
#   "duty": [
#     {
#       "action": "attribute"
#     }
#   ]
# }
#
# consumer = {
#   "@context": "http://www.w3.org/ns/odrl.jsonld",
#   "type": "Offer",
#   "uid": "urn:example:consumer-offer",
#   "assigner": "did:example:consumer-001",
#   "assignee": [
#     "did:example:provider-001"
#   ],
#   "target": [
#     "urn:asset:demo-1"
#   ],
#   "permission": [
#     {
#       "action": "use",
#       "constraint": [
#         {
#           "leftOperand": "odrl:purpose",
#           "operator": "odrl:isAnyOf",
#           "rightOperand": [
#             "productDev",
#             "analytics"
#           ]
#         },
#         {
#           "leftOperand": "odrl:payAmount",
#           "operator": "odrl:lteq",
#           "rightOperand": 3000
#         },
#         {
#           "leftOperand": "odrl:unit",
#           "operator": "odrl:eq",
#           "rightOperand": "USD"
#         },
#         {
#           "leftOperand": "odrl:dateTime",
#           "operator": "odrl:gteq",
#           "rightOperand": "2025-09-03T12:00:00Z"
#         },
#         {
#           "leftOperand": "odrl:dateTime",
#           "operator": "odrl:lteq",
#           "rightOperand": "2025-12-31T12:00:00Z"
#         }
#       ]
#     }
#   ],
#   "duty": [
#     {
#       "action": "obtainConsent"
#     }
#   ]
# }
#
# class TestCatalog(unittest.TestCase):
#
#     def test_initiate_valid(self):
#         class Agent(INegotiator):
#             def on_receive_offer(self, their_policy: Any, t: float):
#                 their_issues = self.adapter.extract_issues(their_policy)
#                 self.opponent_model.update(their_issues)
#                 myU = self.utility.utility(their_issues)
#                 if self.acceptance.accept(myU, t):
#                     return {"type": "ACCEPT", "policy": their_policy, "utility": myU}
#                 new_issues = self.bidding.propose(
#                     my_issues=self.my_issues, opp_last_issues=their_issues, t=t,
#                     U_self=self.utility, U_opp_hat=self.opponent_model.u_hat,
#                     issue_specs=self.specs_map, rng=self.rng,
#                 )
#                 self.my_issues = new_issues
#                 counter = self.adapter.apply_issues(self.base_policy, new_issues)
#                 return {"type": "OFFER", "policy": counter, "utility": self.utility.utility(new_issues)}
#
#             def first_offer(self, t: float = 0.0):
#                 new_issues = self.bidding.propose(
#                     my_issues=self.my_issues, opp_last_issues=None, t=t,
#                     U_self=self.utility, U_opp_hat=self.opponent_model.u_hat,
#                     issue_specs=self.specs_map, rng=self.rng,
#                 )
#                 self.my_issues = new_issues
#                 return {"type": "OFFER", "policy": self.adapter.apply_issues(self.base_policy, new_issues)}
#
#         adapter = ODRLAdapter()
#         specs = adapter.issue_specs(provider)
#         my_issues = adapter.extract_issues(provider)
#         opp_issues = adapter.extract_issues(consumer)
#         weights = build_weights(specs, role="provider")
#         ideals, worsts = _ideals_worsts(specs, my_issues, opp_issues, "provider")
#         U = UtilityModel(specs={s.name: s for s in specs}, weights=weights, ideals=ideals, worsts=worsts)
#
#
#         provider_agent = Agent(
#             name = "provider",
#             base_policy=provider, adapter=ODRLAdapter(), utility=U,
#             acceptance=ProbabilisticThreshold(), bidding=BehaviorMatchingFSJStrategy(),
#             opponent_model=FrequencyOpponentModel()
#         )
#
#         prov_dict = provider_agent.to_dict()
#
#         consumer_agent = Agent.from_dict(prov_dict)
#         consumer_agent.name = "consumer"
#         print(consumer_agent.to_dict())