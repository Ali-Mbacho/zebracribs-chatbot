from typing import Any, Text, Dict, List
from datetime import datetime
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionSearchProperties(Action):
    def name(self) -> Text:
        return "action_fetch_houses"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get all slots at once
        slots = {
            "location": tracker.get_slot("location"),
            "price": tracker.get_slot("price"),
            "date": tracker.get_slot("date"),
            "availability": tracker.get_slot("availability"),
            "property_type": tracker.get_slot("property_type")
        }

        # Check if we have minimal requirements
        if not any(slots.values()):
            dispatcher.utter_message(text="Please tell me something about what you're looking for (location, price, etc.)")
            return []

        try:
            response = requests.get("https://zebracribs.pl/wp-json/wp/v2/properties")
            properties = response.json()
        except requests.exceptions.RequestException:
            dispatcher.utter_message(text="Sorry, I couldn't access the property database.")
            return []

        filtered = self.filter_properties(properties, slots)
        
        if not filtered:
            dispatcher.utter_message(text="No properties match your criteria.")
        else:
            self.send_results(dispatcher, filtered)

        return [SlotSet(slot, None) for slot in slots]  # Clear slots after search

    def filter_properties(self, properties: List[Dict], criteria: Dict) -> List[Dict]:
        results = []
        for prop in properties:
            matches = True
            
            # Location check
            if criteria["location"]:
                if criteria["location"].lower() not in prop.get("content", {}).get("rendered", "").lower():
                    matches = False
            
            # Price check
            if criteria["price"]:
                prop_price = self.extract_price(prop)
                if not prop_price or prop_price > float(criteria["price"]):
                    matches = False
            
            # Availability check
            if criteria["availability"] and "es_status-available" not in prop.get("class_list", []):
                matches = False
                
            if matches:
                results.append(prop)
        
        return results

    def send_results(self, dispatcher: CollectingDispatcher, properties: List[Dict]):
        message = "I found these properties:\n\n"
        for prop in properties[:5]:  # Limit to 5 results
            message += (
                f"🏠 {prop.get('title', {}).get('rendered', 'No title')}\n"
                f"📍 {self.extract_location(prop)}\n"
                f"💰 {self.extract_price(prop)} PLN\n"
                f"🔗 [View details]({prop.get('link')})\n\n"
            )
        dispatcher.utter_message(text=message)