# # This files contains your custom actions which can be used to run
# # custom Python code.

# # See this guide on how to implement these action:
# # https://rasa.com/docs/rasa-pro/concepts/custom-actions


# # This is a simple example for a custom action which utters "Hello World!"

# # import requests
# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker # type: ignore
# from rasa_sdk.executor import CollectingDispatcher # type: ignore
# from rasa_sdk.events import SlotSet # type: ignore





# class ActionFetchHouses(Action):
#     def name(self) -> Text:
#         return "action_fetch_houses"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         location = tracker.get_slot("location")
#         price = tracker.get_slot("price")
#         date = tracker.get_slot("date")
        

#         # Fetch data from the API
#         response = requests.get("https://zebracribs.pl/wp-json/wp/v2/properties")
#         if response.status_code != 200:

#             dispatcher.utter_message(text="Sorry, I couldn't fetch the data at the moment.")
#         # return response.json()
#             return []

#         properties = response.json()
#         filtered_properties = []

#         # Filter properties based on slots
#         for prop in properties:
#             prop_location = prop.get("location", "").lower()
#             prop_price = float(prop.get("price", 0))
#             prop_date = prop.get("available_from", "")

#             if location and location.lower() not in prop_location:
#                 continue
#             if price and float(price) < prop_price:
#                 continue
#             if date and date != prop_date:
#                 continue

#             filtered_properties.append(f"- {prop['title']} for {prop_price} in {prop_location} (Available: {prop_date})")

#         # Respond to the user
#         if filtered_properties:
#             dispatcher.utter_message(text="Here are the available houses:\n" + "\n".join(filtered_properties[:5]))
#         else:
#             dispatcher.utter_message(text="No houses match your criteria.")

#         return [SlotSet("location", None), SlotSet("price", None), SlotSet("date", None)]
#         print(properties)


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionFetchHouses(Action):
    def name(self) -> Text:
        return "action_fetch_houses"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Hardcoded values
        location = "New York"
        date = "2025-03-01"
        
        # Get the user-provided price
        price = tracker.get_slot("price")  # Ensure this slot is in domain.yml

        # Example house listings
        houses = [
            {"id": 1, "price": 500000, "location": location, "date": date},
            {"id": 2, "price": 750000, "location": location, "date": date},
            {"id": 3, "price": 1000000, "location": location, "date": date},
        ]

        # Filter houses based on price if given
        if price:
            try:
                price = int(price)
                houses = [h for h in houses if h["price"] <= price]
            except ValueError:
                dispatcher.utter_message(text="Invalid price value.")
                return []

        # Format response
        if houses:
            house_list = "\n".join([f"- House {h['id']}: ${h['price']}" for h in houses])
            message = f"Here are some houses in {location} (Date: {date}):\n{house_list}"
        else:
            message = f"No houses found under ${price} in {location}."

        dispatcher.utter_message(text=message)
        return []
