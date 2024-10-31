from ExampleAgency.ExampleAgent import ExampleAgent
from dotenv import load_dotenv
from agency_swarm import Agency

load_dotenv()


agency = Agency(
    agency_chart=[ExampleAgent()],
)


if __name__ == "__main__":
    print(agency.get_completion("Hello, how are you?"))
