# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from fractions import Fraction
from pdb import Restart
from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet, ActiveLoop
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import UserUtteranceReverted, AllSlotsReset
from rasa_sdk.events import AllSlotsReset, SessionStarted
from typing import Any, Text, Dict, List
import json

import logging 
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import aiohttp

class ActionReturnIntentAndEntity(Action):
    def name(self) -> Text:
        return "action_return_intent_and_entity"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info("Action triggered.")
        latest_message = tracker.latest_message
        user_intent = latest_message['intent'].get('name')
        intent_confidence = latest_message['intent'].get('confidence')
        user_entities = latest_message['entities']

        response_data = {
            "intent": user_intent,
            "confidence": intent_confidence,
            "entities": user_entities if user_entities else []
        }

        logging.info(f"Response Data: {response_data}")
        dispatcher.utter_message(text=str(response_data))
        logging.info("Response sent to dispatcher.")
        return []

class ValidateBuyStockForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_buy_stock_form"

    def validate_stock_symbol(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        # Kiểm tra mã cổ phiếu: 3-5 ký tự, chỉ chữ cái
        if not value.isalpha() or len(value) < 3 or len(value) > 5:
            dispatcher.utter_message(
                json_message={
                    "intent": "form",
                    "required_slot": "stock_symbol",
                    "error": "Mã cổ phiếu phải gồm 3-5 chữ cái (ví dụ: VNM, ACB)."
                }
            )
            return {"stock_symbol": None}
        return {"stock_symbol": value.upper()}  # Trả về chữ in hoa

    def validate_amount(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        try:
            amount = float(value)
            if amount <= 0:
                dispatcher.utter_message(
                    json_message={
                        "intent": "form",
                        "required_slot": "amount",
                        "error": "Số lượng phải lớn hơn 0."
                    }
                )
                return {"amount": None}
            return {"amount": amount}
        except ValueError:
            dispatcher.utter_message(
                json_message={
                    "intent": "form",
                    "required_slot": "amount",
                    "error": "Vui lòng nhập số (ví dụ: 100, 50.5)."
                }
            )
            return {"amount": None}


class ActionSubmitBuyStockForm(Action):

    def name(self) -> Text:
        return "action_submit_buy_stock_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        stock_symbol = tracker.get_slot("stock_symbol")
        amount = tracker.get_slot("amount")

        # Thông báo kết quả qua JSON
        response_data = {
            "intent": "submit_form",
            "slots": {
                "stock_symbol": stock_symbol,
                "amount": amount
            },
            "success": True,
            "message": f"Bạn đã đặt lệnh mua {amount} cổ phiếu {stock_symbol}."
        }

        # Gửi phản hồi dưới dạng JSON
        dispatcher.utter_message(text=json.dumps(response_data))

        return []
    
class ValidateSellStockForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_sell_stock_form"

    def validate_stock_symbol(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        # Add validation logic for stock_symbol (e.g., check if it's a valid stock)
        # Example: Ensure stock symbol is alphabetic and 3-5 characters
        if not value.isalpha() or len(value) < 3 or len(value) > 5:
            response_data = {
                "intent": "form",
                "required_slot": "stock_symbol",
                "error": "Mã cổ phiếu phải gồm 3-5 chữ cái (ví dụ: VNM, ACB)."
            }
            dispatcher.utter_message(text=json.dumps(response_data))
            return {"stock_symbol": None}
        return {"stock_symbol": value.upper()}  # Return uppercase stock symbol

    def validate_amount(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        try:
            # Convert the value to a float
            amount = float(value)
            if amount <= 0:
                response_data = {
                    "intent": "form",
                    "required_slot": "amount",
                    "error": "Số lượng phải lớn hơn 0."
                }
                dispatcher.utter_message(text=json.dumps(response_data))
                return {"amount": None}  # Ensure it asks again
            return {"amount": amount}
        except ValueError:
            response_data = {
                "intent": "form",
                "required_slot": "amount",
                "error": "Vui lòng nhập số (ví dụ: 100, 50.5)."
            }
            dispatcher.utter_message(text=json.dumps(response_data))
            return {"amount": None}  # Ensure it asks again

class ActionSubmitSellStockForm(Action):

    def name(self) -> Text:
        return "action_submit_sell_stock_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        stock_symbol = tracker.get_slot("stock_symbol")
        amount = tracker.get_slot("amount")

        # Nếu thiếu slot hoặc slot không hợp lệ, trả về lỗi
        if not stock_symbol or not amount:
            response_data = {
                "intent": "submit_form",
                "slots": {
                    "stock_symbol": stock_symbol,
                    "amount": amount
                },
                "success": False,
                "message": "Thông tin không hợp lệ. Vui lòng kiểm tra lại mã cổ phiếu và số lượng."
            }
            dispatcher.utter_message(text=json.dumps(response_data))
            return []

        # Trả về JSON xác nhận giao dịch thành công
        response_data = {
            "intent": "submit_form",
            "slots": {
                "stock_symbol": stock_symbol,
                "amount": amount
            },
            "success": True,
            "message": f"Bạn đã đặt lệnh bán {amount} cổ phiếu {stock_symbol}."
        }
        dispatcher.utter_message(text=json.dumps(response_data))

        return []

    
class ActionResetForm(Action):
    def name(self) -> str:
        return "action_reset_form"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]

class ActionDefaultFallback(Action):
    def name(self) -> str:
        return "action_default_fallback"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Xin lỗi, tôi không hiểu. Bạn có thể nói rõ hơn không?")
        return [UserUtteranceReverted()]
    

class ActionRestart(Action):
    def name(self):
        return "action_restart"

    def run(self, dispatcher, tracker, domain):
        # Reset tất cả các slot và bắt đầu lại phiên hội thoại
        dispatcher.utter_message(text="Conversation has been restarted.")
        return [AllSlotsReset(), SessionStarted()]
    
class ActionSwitchForm(Action):
    def name(self) -> Text:
        return "action_switch_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Lấy intent hiện tại của người dùng
        current_intent = tracker.get_intent_of_latest_message()

        # Lấy form hiện tại
        current_form_name = tracker.active_loop.get("name") if tracker.active_loop else None

        # Kiểm tra nếu người dùng đang ở đúng form rồi
        if (current_form_name == "buy_stock_form" and current_intent == "buy_form") or \
           (current_form_name == "sell_stock_form" and current_intent == "sell_form"):
            response_data = {
                "intent": "switch_form",
                "from_form": current_form_name,
                "to_form": current_form_name,
                "success": False,
                "message": "Bạn đã ở đúng form rồi, không cần chuyển đổi."
            }
            dispatcher.utter_message(text=json.dumps(response_data))
            return []

        # Reset các slots liên quan đến form hiện tại
        events = [
            SlotSet("stock_symbol", None),
            SlotSet("amount", None),
            ActiveLoop(None)  # Hủy form hiện tại
        ]

        # Kích hoạt form mới dựa trên intent
        if current_form_name == "buy_stock_form":
            events.append(ActiveLoop("sell_stock_form"))
            response_data = {
                "intent": "switch_form",
                "from_form": "buy_stock_form",
                "to_form": "sell_stock_form",
                "success": True,
                "message": "Đã chuyển sang form bán cổ phiếu."
            }
            dispatcher.utter_message(text=json.dumps(response_data))

        elif current_form_name == "sell_stock_form":
            events.append(ActiveLoop("buy_stock_form"))
            response_data = {
                "intent": "switch_form",
                "from_form": "sell_stock_form",
                "to_form": "buy_stock_form",
                "success": True,
                "message": "Đã chuyển sang form mua cổ phiếu."
            }
            dispatcher.utter_message(text=json.dumps(response_data))

        return events