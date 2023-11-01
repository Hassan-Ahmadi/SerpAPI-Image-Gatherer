"""
Google Image Search and Database Storage Script

This script allows you to search for images on Google using the SerpApi service and store the downloaded images in a PostgreSQL database.

Prerequisites:
- Ensure that you have the required Python libraries installed (aiohttp, psycopg2, dotenv).
- Set up your SerpApi API key and PostgreSQL database connection details in environment variables or provide them interactively.

Usage:
1. Run the script.
2. Enter a search query, the maximum number of images to download, and your SerpApi API key when prompted.
3. The script will fetch image results from Google using SerpApi, download the images, and store them in the database.
4. You can exit the script by typing 'exit' as the search query.

Please make sure to set your SerpApi API key and PostgreSQL connection details in environment variables or provide them when prompted.

"""

import asyncio
import aiohttp
import psycopg2
from io import BytesIO
from pprint import pprint
import dotenv
import os
import time


async def get_database_parameters():
    """
    Prompt the user for PostgreSQL database connection parameters or
    use values from environment variables.

    Returns:
    dict: A dictionary containing PostgreSQL connection parameters.
    """

    db_params = dict()

    if not os.environ.get("DB_HOST"):
        db_params["host"] = input("Please enter host: ")
    else:
        db_params["host"] = os.environ.get("DB_HOST")

    if not os.environ.get("DB_NAME"):
        db_params["database"] = input("Please enter database name: ")
    else:
        db_params["database"] = os.environ.get("DB_NAME")

    if not os.environ.get("DB_USER"):
        db_params["user"] = input("Please enter database user name: ")
    else:
        db_params["user"] = os.environ.get("DB_USER")

    if not os.environ.get("DB_PASSWORD"):
        db_params["password"] = input("Please enter database user password: ")
    else:
        db_params["password"] = os.environ.get("DB_PASSWORD")

    if not os.environ.get("DB_PORT"):        
        db_params["port"] = input("Please enter database port: ")
    else:
        db_params["port"] = int(os.environ.get("DB_PORT"))

    return db_params


async def create_database_connection(db_params):
    """
    Create a connection to the PostgreSQL database using provided parameters.

    Args:
    db_params (dict): PostgreSQL connection parameters.

    Returns:
    tuple: A tuple containing the database connection and cursor.
    """

    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        return connection, cursor
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return None, None


async def init_db(connection, cursor):
    """
    Initialize the database by creating the 'images' table if it doesn't exist.

    Args:
    connection: psycopg2 database connection.
    cursor: psycopg2 database cursor.
    """

    try:
        # Define the SQL query to create the "images" table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS images (
            id serial PRIMARY KEY,
            name VARCHAR(255),
            data BYTEA
        );
        """

        cursor.execute(create_table_query)
        connection.commit()

        print("Table 'images' created successfully.")

    except psycopg2.Error as e:
        print(f"Error: {e}")


async def get_serpapi_api_key():
    """
    Prompt the user for their SerpApi API key or use a default key from environment variables.

    Returns:
    str: SerpApi API key.
    """

    if not os.environ.get("SERPAPI_API_KEY"):
        return input(
            "Please enter your SerpApi API key(press enter to use default api key): "
        )
    else:
        return os.environ.get("SERPAPI_API_KEY")


async def download_image(session, url, timeout=5):
    """
    Download an image from a URL using aiohttp.

    Args:
    session: aiohttp ClientSession.
    url (str): URL of the image to download.
    timeout (int): Request timeout (in seconds).

    Returns:
    bytes: Image data if successful, None if an error occurs.
    """

    try:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                return await response.read()
            else:
                print(f"Error: HTTP status code {response.status} for URL: {url}")
                return None
    except Exception as e:
        print(f"Error for URL {url}: {e}")
        return None


def store_image_in_database(connection, cursor, name, data):
    """
    Store an image in the PostgreSQL database.

    Args:
    connection: psycopg2 database connection.
    cursor: psycopg2 database cursor.
    name (str): Name of the image.
    data (bytes): Image data.
    """

    if connection and cursor:
        try:
            cursor.execute(
                "INSERT INTO images (name, data) VALUES (%s, %s);",
                (name, psycopg2.Binary(data)),
            )
            connection.commit()
            print(f"Stored {name} to db")
        except psycopg2.Error as e:
            print(f"Error: {e}")


async def get_images_urls(session, api_key, query, max_images):
    """
    Fetch image URLs from SerpApi based on a search query.

    Args:
    session: aiohttp ClientSession.
    api_key (str): SerpApi API key.
    query (str): Search query.
    max_images (int): Maximum number of images to fetch.

    Returns:
    list: List of image results from SerpApi.
    """

    async with session.get(
        f"https://serpapi.com/search.json?q={query}&tbm=isch&key={api_key}"
    ) as response:
        if response.status == 200:
            data = await response.json()
            return data["images_results"][:max_images]
        else:
            print(f"Error: {response.status}")
            return []


async def download_store_image(results, session, connection, cursor):
    """
    Download and store a list of images.

    Args:
    results (list): List of image results.
    session: aiohttp ClientSession.
    connection: psycopg2 database connection.
    cursor: psycopg2 database cursor.
    """

    download_tasks = []

    for i, result in enumerate(results):
        image_url = result["thumbnail"]
        print(f"{[i + 1]} downloading {image_url}")
        download_task = download_image(session, image_url)
        download_tasks.append(download_task)

    downloaded_images = await asyncio.gather(*download_tasks)

    for i, image_data in enumerate(downloaded_images):
        if image_data:
            store_image_in_database(connection, cursor, f"image_{i+1}.jpg", image_data)


async def main():
    """
    Main entry point of the script. Handles user input and execution of the script.
    """
    print(
        "This script allows you to search for images in google and store them in database."
    )

    print("looking for .env ...")
    dotenv.load_dotenv(dotenv.find_dotenv())

    db_params = await get_database_parameters()
    connection, cursor = await create_database_connection(db_params)
    await init_db(connection, cursor)

    api_key = await get_serpapi_api_key()

    async with aiohttp.ClientSession() as session:
        while True:
            query = input("\nEnter the search query (or 'exit' to quit): ")
            if query.lower() == "exit":
                break

            max_images = int(
                input("Enter the maximum number of images to download[1-100]: ")
            )
            if 100 < max_images < 1:
                print("Wrong value!")
                continue

            print(f"please wait a few seconds...")

            start_time = time.time()  # Start timing

            async with aiohttp.ClientSession() as session:
                results = await get_images_urls(session, api_key, query, max_images)
                if len(results) > 0:
                    print(f"Found {len(results)} results")

                    await download_store_image(results, session, connection, cursor)
                    print("-" * 40)
                    print(
                        f"Downloaded and stored {max_images} results in {round(time.time() - start_time,2)}"
                    )
                else:
                    print(f"No result found!")

        # closing database
        cursor.close()
        connection.close()


if __name__ == "__main__":
    asyncio.run(main())
