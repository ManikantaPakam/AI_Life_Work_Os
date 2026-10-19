from agents import build_agents
from database import initialize_database


def main():
    initialize_database()
    agents = build_agents()
    print("\nAI Life & Work OS")
    print("Type 'exit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue
        try:
            result = (agents["supervisor"].invoke({"messages": [{"role": "user","content": user_input,}]}))
            messages = result.get("messages",[],)
            if messages:
                print("\nAssistant:",messages[-1].content,)
            else:
                print("\nAssistant: "
                    "No response.")
        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()