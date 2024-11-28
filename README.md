# Welcome to My Projects Page!

## About

I'm currently learning PHP, HTML, and CSS, and this projects page serves as a showcase of my progress and experimentation with these technologies. Here, you'll find various projects that I've worked on as part of my learning journey. Each project represents a different aspect of my learning process and highlights the skills and techniques I've been exploring.

## Projects

- **Project Name**: [Alternative Syntax for Control Structures]
  - **Description**: [A simple page with alternative syntax for control structures.]
  - **Technologies Used**: PHP, HTML, CSS
 
  - **Project Name**: [Snake Game]
  - **Description**: [A fun Snake Game from another coder]
  - **Technologies Used**: JavaScript, HTML, CSS

  - **Project Name**: [Label Generator Web Application]
  - **Description**: [A web-based label generator that creates labels with text and UPC barcodes.]
  - **Technologies Used**: PHP, HTML, CSS

  - **Setup Instructions**:
    1. PHP 7.4 or higher with GD extension enabled
    2. Composer (PHP package manager)
    3. Web server (Apache, Nginx, or PHP's built-in server)

  - **Setup Steps**:
    1. **Install Composer**
       - Download Composer installer from [https://getcomposer.org/download/](https://getcomposer.org/download/)
       - Run the installer (Composer-Setup.exe)
       - Follow the installation wizard
       - After installation, close and reopen any command prompts

    2. **Install Dependencies**
       - Open a command prompt
       - Navigate to the project directory
       - Run: `composer install`
       - This will create the `vendor` directory with all required packages

    3. **Font Setup**
       - Place the following font files in the project directory:
         - `arial.ttf`
         - `arialbd.ttf`
       - You can copy these from your Windows fonts directory: `C:\Windows\Fonts`

    4. **Start the Server**
       - Open a command prompt
       - Navigate to the project directory
       - Run: `php -S localhost:8000`
       - Open your web browser and go to: `http://localhost:8000`

  - **Usage**:
    1. Fill in the required fields:
       - Name Line 1 (required)
       - Name Line 2 (optional)
       - Variant (required)
       - UPC Code (12 digits, required)

    2. Click "Generate Label" to create and preview the label

    3. Use the "Print Label" button to print the generated label

  - **Files**:
    - `index.html`: Web interface
    - `label.php`: Label generation logic
    - `composer.json`: PHP dependencies configuration

  - **Troubleshooting**:
    1. If you see an error about `vendor/autoload.php`:
       - Make sure you've run `composer install`
       - Check if the `vendor` directory exists in your project

    2. If the label text doesn't appear:
       - Verify that the font files are in the correct location
       - Check PHP error logs for font-related errors

    3. If the barcode doesn't generate:
       - Ensure you've entered exactly 12 digits
       - Verify that the Picqer barcode package was installed correctly

<!--(Repeat the above structure for each project)-->

## How to Use

Feel free to explore the projects listed above. Each project may include its own README file with instructions on how to run or interact with it. If you have any questions or feedback, please don't hesitate to reach out!

## Getting Started

To get started, simply clone this repository to your local machine:

Then, navigate to the directory containing the projects and open them in your preferred code editor to explore the code and make changes as needed.

## Contributing

If you're interested in contributing to any of the projects or have suggestions for improvements, feel free to fork the repository and submit a pull request with your changes. Contributions are always welcome!

## Contact

If you have any questions, feedback, or just want to say hi, you can reach me at [help@latinospc.com].

Happy coding!
