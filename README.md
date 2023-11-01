# Google Image Search and Database Storage Script

This script allows you to search for images on Google using the SerpApi service and store the downloaded images in a PostgreSQL database.

## Getting Started

These instructions will help you set up a virtual environment, install the necessary dependencies, and run the script on your local machine.

### Prerequisites

- Python 3.7 or higher
- `venv` (Python's built-in virtual environment module)

### Setup Virtual Environment

1. Open your terminal and navigate to the project directory.

2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:

    - On Windows:

    ```bash
    .\venv\Scripts\activate
    ```

    - On macOS and Linux:

    ```bash
    source venv/bin/activate
    ```

### Installing Dependencies

1. Make sure your virtual environment is activated.

2. Install the required Python packages using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Script

1. Make sure your virtual environment is activated.

2. Run the script:

    ```bash
    python main.py
    ```

3. Follow the on-screen prompts to enter the search query and other details.

4. The script will search for images, download them, and store them in the database.

## Environment Variables

- You can set environment variables to provide the SerpApi API key and database connection details without entering them each time. Create a `.env` file in your project directory with the following content:

    ```
    SERPAPI_API_KEY=your_serpapi_api_key
    DB_HOST=your_db_host
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    ```

## Usage

- Follow the on-screen instructions to search for images and store them in the database.

- Type 'exit' to quit the script.

## Contributing

If you'd like to contribute to this project, feel free to open an issue or create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.