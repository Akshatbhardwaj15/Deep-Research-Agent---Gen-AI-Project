from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipelin(topic :  str) -> dict:

    state = {}

    #search agent working
    print("\n"+" ="*50)
    print("step 1 - search agent is working....")
    print("="*50)

    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state["search_results"] = search_results['messages'][-1].content
    
    print("\n search agent result:\n", state["search_results"])
    
    
    #reader agent
    print("\n" + " ="*50)
    print("step 2 : reader agent fetching and summarizing the content")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_results = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_results['messages'][-1].content

    print("\n Scraped content: \n", state['scraped_content'])


    #step - 3

    print("\n" + " ="*50)
    print("step 3 - writer agent writing the report")
    print(" ="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic ,
        "research" : research_combined
    })

    print("\n Final Report\n", state['report'])

    #critic report

    print("\n"+"*"*50)
    print("step 4 - critic agent criticing the report")
    print("*"*50)

    state["feedback"] = critic_chain.invoke({
        "report" : state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state


if __name__ == "__main__":
    topic = input("Enter topic for research : ")
    result = run_research_pipelin(topic)

