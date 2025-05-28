flash - Admin Guide
===================

## Adding a scraped feed

Certain sites lack an RSS feed. For these generate locally a config for mkfd as follows.

Start he service locally:

    docker-compose -f docker-compose.local.yml up mkfd

Now open http://localhost:5000/ and define the config.

Assuming a3db0357d90b is the CONTAINER ID of mkfd (find out with `docker ps`), and `72365d96-68ec-4692-a0c2-22008f734f53` is the id of the new feed, copy the file to your host:

    docker cp a3db0357d90b:/app/configs/72365d96-68ec-4692-a0c2-22008f734f53.yaml .

Then, assuming `mkfd-7497cf55d-6w2zk` is the name of the mkfd service (find out with `kubectl -n flash get pods`), copy over the file:

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
