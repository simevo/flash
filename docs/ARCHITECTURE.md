flash - Architecture Overview
=============================

## Overall Project Architecture

This section describes the overall architecture of the Flash project, including the backend (Django), frontend (Vue.js), and other services. 

The architecture is the classical **three-tier** architecture for webapps:

![architecture](./architettura.svg "Architecture")

The **front-end** (1) is implemented in HTML5 with:

- the [Bootstrap CSS framework](https://getbootstrap.com/) version 5 (currently in beta)

- the [Babel JavaScript transpiler](https://babeljs.io/) to convert from JavaScript ES6 source code into "compiled" ES5 code that can be grokked by any browser

- and [Vue.js front end JavaScript framework](https://vuejs.org/) version 2.

The **back-end** (2) is implemented in the Python 3.9 language as an "API only" [Django](https://www.djangoproject.com/) project based on [Django REST framework (DRF)](https://www.django-rest-framework.org/); there are no app forms/visual interfaces except the admin interface and the API playground provided by DRF.

The **data-base** (3) reuses the existing PostgreSql database, with minimal changes to the tables as required by Django.

This architecture allows us to get the best out of Django (for the database interface, data types and API structure), while keeping the app UI reactive and fast.


## Database schema

The Entity-Relationship diagram of the main tables and their relationships is:

![Entity-Relationship diagram](er-diagram.png)

The two main tables are `feeds` and `articles`. Each of them has a supplementary table for expensive-to-compute values (`feeds_data` and `articles_data` respectively) which are "manual", pseudo materialized views, selectively refreshed by triggers that react on the input data processed by the `feeds_data_view` and `articles_data_view` (not shown on the diagram).

Many articles can be aggregated from a single feed, therefore the two tables are linked by a one-to-many relationship from `feed.id` to `articles.feed_id`.

Feeds can be rated by users, whereas articles can be rated, read and dismissed. These user - feed/article many-to-many relationships are stored through the `news_userfeeds` and `news_userarticles` tables.

Additionally users can bookmark articles in separate lists, or get different automatic newsfeeds. To flexibly handle all these different lists, the lists metadata are stored in the `news_userarticleslists` table with a one-to-many relationship from `users_user.id` to `news_userarticleslists.user_id`. The actual article lists (which are many-to-many relationships between the `articles` and the `news_userarticleslists` tables) are stored though the `news_userarticles` table.
