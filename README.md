# OctoRadar: GitHub Data Visualization

OctoRadar is a web application that fetches GitHub data, stores it in a MongoDB database, and presents insightful statistics and information through a user-friendly web interface. Gain a comprehensive view of your GitHub organizations and repositories with this powerful tool.

## Features

- Fetch GitHub organizations and projects data
- Store data in a MongoDB database
- Render GitHub statistics through a dynamic web UI
- Explore insightful charts and graphs for better understanding
- User-friendly interface for convenient GitHub information retrieval

## Table of Contents

- [Setup Instructions](#setup-instructions)
- [Contributing](#contributing)
- [License](#license)

## Setup Instructions

Run the following command to deploy your local stack

    ```bash
    docker compose up --build
    ```

    Docker Swarm is a container orchestration tool built into Docker. It allows you to manage multiple containers as a single service.

3. **Deploy the stack:** In the root directory of the project, there is a file called `docker-compose.yml`. This file defines the services that make up your application. Deploy these services as a stack on Docker Swarm using the following command:

    ```bash
    docker stack deploy -c docker-compose.yml my_stack
    ```

    Replace `my_stack` with the name you want to give to your stack.

To remove the stack and stop the services, use the following command:

```bash
docker stack rm my_stack
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.

Make sure to run flake8 before pushing your changes. There shouldn't be any warnings.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

** This project is under development.