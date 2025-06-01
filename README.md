# flash

An open-source news platform with aggregation and ranking.

Second iteration born from the ashes of [**calo.news** ("An open-source news platform with aggregation, ranking and conversations")](https://gitlab.com/simevo/calo.news), sharing a similar Postgres DB structure but:

- without PHP
- based on a modern Python web framework (Django and Django REST Framework) for the back-end
- using TypeScript and an up-to-date vite-based tooling for the Vue.js front-end
- and ready for deployment on a Kubernetes cluster.

## Documentation

For detailed information, please refer to the following documents:

- [User Guide](docs/USING.md)
- [Admin Guide](docs/ADMIN.md)
- [Developer Guide](docs/DEVELOPING.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

The full documentation, built with Sphinx, can be accessed [here](docs/_build/html/index.html) (requires building the docs locally).

## Project Structure

- `compose/`: Contains Docker Compose configurations for local development and production environments.
- `config/`: Holds project-level Django configurations, such as settings (`settings.py`), root URL patterns (`urls.py`), and WSGI application (`wsgi.py`).
- `docs/`: Contains project documentation source files (Sphinx and Markdown).
- `flash/`: Main Django application directory. It includes:
    - `static/`: Project-wide static assets (CSS, JavaScript, images).
    - `templates/`: Project-wide Django HTML templates.
    - `users/`: Django app for user management, authentication, and profiles.
- `frontend/`: Houses the Vue.js frontend application code.
- `news/`: Django app responsible for news aggregation, articles, feeds, and related models and views.
- `requirements/`: Stores Python dependency files for different environments (e.g., `base.txt`, `local.txt`, `production.txt`).

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) to learn how you can help.

## License

**flash** an open-source news platform with aggregation and ranking

Copyright (C) 2017-2025 Paolo Greppi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program (file [LICENSE](/LICENSE)).
If not, see <https://www.gnu.org/licenses/>.
