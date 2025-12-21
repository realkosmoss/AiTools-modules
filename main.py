from curl_cffi import requests
from services.perchance_org import Perchance, PerchanceContext

def main():
    session = ... # cmon you can make your own one

    pchance = Perchance(session)

    test_chat = []
    
    PC = PerchanceContext(
        loreData="we are in parking lot smoking crack",
        Username="man",
        UserDescription="Im just a man.",
        BotName="girl",
        BotDescription="im girl, i like man."
    )

    print("Starting loop.")
    while True:
        UserInput = input("Message: ")
        test_chat.append({
            "role": "user",
            "content": UserInput
        })
        BotResponse = pchance.generate(test_chat, PC)
        print("Response:", BotResponse)
        test_chat.append({
            "role": "assistant",
            "content": BotResponse
        })

if __name__ == "__main__":
    main()