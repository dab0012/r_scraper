import requests
import random
from bs4 import BeautifulSoup
from colorama import Fore, Style


# Class to handle HTTP requests in a more transparent way in scraping and denial of service environments
# by the servers from which the data is requested
# Basically, it manages the proxies and user agents so that scraping is not detected
#
# Usage example:
# request_handler = RequestHandler()
# response = request_handler.do_request('https://www.google.com')
#
# Author: Daniel Alonso Báscones (@dnllns)
# Date: 2022-12-23
# Project: TFG OLIVIA

class RequestHandler(requests.Request):


    # Class constructor
    def __init__(self, max_request=5, *args, **kwargs):


        # Call the constructor of the parent class
        super().__init__(*args, **kwargs)

        # Initialize the proxy list
        self.proxies = {}

        # Initialize the user agent list
        self.user_agents = []

        # Maximum number of requests to be made with the same proxy
        self.max_request = max_request

    # Get proxies from proxyscrape.com API using the free plan and save them in the proxy list
    def __obtain_proxies(self) -> None:

        # get proxy
        proxies = requests.get('https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all').text
        proxies = proxies.splitlines()

        # Save (proxy, number_uses) in proxy list
        self.proxies = [(f'http://{proxy}', 0) for proxy in proxies]

    # Get next proxy
    def __get_next_proxy(self) -> dict[str, str]:
        '''
        Get a random proxy from the proxy list
        
        Returns:
            dict: Dictionary with the selected proxy
        '''

        # If the proxy list is empty, get new proxies
        if not self.proxies:
            self.__obtain_proxies()

        # Select the next proxy
        selected_proxy, num_usages = self.proxies[0]

        # If the proxy has already been used the specified number of times, remove it from the proxy list
        num_usages+=1
        if num_usages == self.max_request:

            # Remove the tuple proxy from the proxy list
            self.proxies.remove(
                (selected_proxy, num_usages-1)
            )

        # If not, update the number of proxy uses
        else:
            self.proxies[0] = (selected_proxy, num_usages)

        # return proxy
        return { 'http': selected_proxy }

    # Get user agents from the useragentstring.com API
    def __obtain_user_agents(self, max_count=30) -> None:
        '''
        Get user agents from the useragentstring.com API
        '''
        # Obtener user agents
        user_agents_request = requests.get('https://www.useragentstring.com/pages/useragentstring.php?name=All').text
        soup = BeautifulSoup(user_agents_request, 'html.parser')

        # Find the div element with id = liste
        div = soup.find(id="liste")

        # Search for all li elements within the div element
        lis = div.find_all("li")

        # Stores user agents in a list
        count = 0
        for li in lis:

            # You only get the first 30 user agents
            if count == max_count:
                break
            # Extracts the text of each li element
            user_agent = li.text

            # Add the user agent to the list
            self.user_agents.append(user_agent)
            count+=1

    # Get a random user agent from the user agent list
    def __get_random_user_agent(self) -> dict[str, str]:
        '''
        Obtener un user agent aleatorio
        
        Returns:
            str: User agent
        '''
        # Si la lista de user agents está vacía, obtener nuevos user agents
        if self.user_agents == []:
            self.__obtain_user_agents()

        # Seleccionar un user agent aleatorio
        selected_user_agent = random.choice(self.user_agents)

        # Eliminar el user agent de la lista
        self.user_agents.remove(selected_user_agent)

        return {'User-Agent': selected_user_agent}

    # Make an HTTP request
    def do_request(self, url, retry = False) -> bytes:
        '''
        Make an HTTP request

        args:
            url (str): URL of the request

        Returns:
            bytes: HTML of the response
        '''
    
        # Get proxy and user agent
        proxy = self.__get_next_proxy()
        user_agent = self.__get_random_user_agent()

        # Make HTTP request
        response = requests.get(url, proxies=proxy, headers=user_agent, timeout=10)

        if retry:
            retry_count = 0

            # If the request fails, retry it
            while response.status_code != 200:

                # Color red
                print(Fore.RED)
                print("Request failed:")
                print("Proxy: ", proxy)
                print("User agent: ", user_agent)
                print("URL: ", url)
                print("Status code: ", response.status_code)
                print("Retrying request. Times: ", retry_count)
                response = requests.get(url, proxies=proxy, headers=user_agent, timeout=10)

                # If the request fails 5 times in a row, change the proxy and user agent
                if retry_count % 5 == 0:
                    print("Request failed 5 times. Changing proxy and user agent")
                    proxy = self.__get_next_proxy()
                    user_agent = self.__get_random_user_agent()

                # Color reset
                print(Style.RESET_ALL)
                
                # Increment retry count
                retry_count+=1

        # return HTML
        return response
    
