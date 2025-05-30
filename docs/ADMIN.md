flash - Admin Guide
===================

## Adding a scraped RSS feed

Certain sites lack an RSS feed. For these generate locally a config for mkfd as follows.

Start the service locally:

    docker-compose -f docker-compose.local.yml up mkfd

Now open http://localhost:5000/ and define the config.

Assuming a3db0357d90b is the CONTAINER ID of mkfd (find out with `docker ps`), and `72365d96-68ec-4692-a0c2-22008f734f53` is the id of the new feed, copy the file to your host:

    docker cp a3db0357d90b:/app/configs/72365d96-68ec-4692-a0c2-22008f734f53.yaml .

Then, assuming `mkfd-7497cf55d-6w2zk` is the name of the mkfd service pod (find out with `kubectl -n flash get pods`), copy over the file:

    kubectl cp 72365d96-68ec-4692-a0c2-22008f734f53.yaml flash/mkfd-7497cf55d-6w2zk:/configs/.

and restart the service by kiiling the pod:

    kubectl -n flash delete pod mkfd-7497cf55d-6w2zk

Verify that the RSS feed is generated with:

    kubectl -n flash exec flash-6dd97d9dcc-s4rgm -- curl http://mkfd:5001/public/feeds/72365d96-68ec-4692-a0c2-22008f734f53.xml
 
## Detecting duplicates

The command `find_duplicates` can be used to detect duplicate articles. It accepts as options arguments:

- a threshold which is the minimum similarity score required to consider two articles as duplicates
- a minimum article ID to process

The command will output a list of duplicate sets, where each set contains articles that are considered duplicates.

Example:

    kubectl -n flash exec flash-6dd97d9dcc-s4rgm -- python manage.py find_duplicates 0.01 4000000

## Feed Polling Statistics

The system automatically records statistics for each attempt to poll an RSS feed. This information can be valuable for administrators to monitor the health and performance of different feeds.

The following data is recorded for each poll attempt:

- **Feed**: The feed that was polled.
- **Poll Start Time**: The timestamp when the polling for this feed began.
- **Poll End Time**: The timestamp when the polling for this feed finished.
- **HTTP Status Code**: The HTTP status code received when attempting to fetch the feed (e.g., 200 for success, 404 for not found, 500 for server error).
- **Articles Retrieved**: The number of articles successfully identified and retrieved from the feed content.
- **Articles Failed**: The number of articles that were identified but could not be processed or stored due to errors.
- **Articles Stored**: The number of new, unique articles that were successfully stored in the database.

These statistics are accessible for staff users in the feed datil page, under the exandable section "Monitoraggio".

Some tips for interpreting them:

- Frequent Errors (non-200 HTTP Status Codes): May indicate that a feed URL is broken, has moved, the server is unreliable or just throttling automated requests.
- Low "Articles Retrieved" or "Articles Stored": Could suggest issues with the article retrieval, or that the feed content is not changing frequently.
- High "Articles Failed": Points to problems in processing articles from that feed, possibly due to unexpected content structure.
- Long polling times (difference between "Poll End Time" and "Poll Start Time"): Could indicate a slow or unresponsive feed source.
