#This is a demo that showcases CrewAI's AI Agents. 
#This is similar to AutoGen but has more fine control

#uncomment the import below for local Ollama instead of ChatGPT4
from langchain.llms import Ollama 
from crewai import Agent, Task, Crew, Process
import os

#Set this if you have an OpenAI key for GPT4 and uncomment
#print("Please paste your openAPI key here:")
#openapikey = input()
#os.environ["OPEN_API_KEY"]= openapikey

#uncomment the import below for local Ollama instead of ChatGPT4
ollama_openhermes=Ollama(model="openhermes")

researcher = Agent(
    role="researcher",
    goal="research new AI insights",
    backstory="You are an AI research assistant",
    verbose=True,
    allow_delegation=False,
    llm=ollama_openhermes 
    )
writer = Agent(
    role="writer",
    goal="write a compelling blog post about new AI insights",
    backstory="You are a AI blog post writer who writes about current trends in AI",
    verbose=True,
    allow_delegation=False,
    llm=ollama_openhermes 
    )

task1=Task(description="Investigate the latest AI trends", agent=researcher)
task2=Task(description="Write a blog post about the latest AI trends", agent=writer)
crew=Crew(agents=[researcher,writer],
    tasks=[task1,task2],
    verbose=2,
    process=Process.sequential
    )
result=crew.kickoff()
print(result)

