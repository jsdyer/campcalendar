# Camp Calendar

[Open Camp Calendar](https://coolcode.ca/campcalendar/)

<!-- coolcode:guide -->
Select July, RV and Friday or Saturday to compare the booking lead time at Rissers Beach with Graves Island. The percentile range covers the middle half of successful bookings.
<!-- /coolcode:guide -->

## Reading the records

The importer streams the provincial reservation CSV. It includes ordinary campsites with a tent or RV, at least one booked night, a parseable arrival date and a creation date on or before arrival. It treats Friday and Saturday arrivals as weekend starts. The published snapshot groups reservations by park, arrival month, equipment and arrival-day group. Individual booking records and customer fields stay out of the browser dataset.

Quantiles use the nearest-rank convention, so each displayed day is an observed lead time. The bar denominators are all qualifying records for each selected park. The tool cannot measure unfilled sites or unsuccessful searches. All covered years are pooled.

## Data and updates

[Nova Scotia provincial park reservations](https://data.novascotia.ca/datasets/4zt7-x443) supplies the underlying records. A monthly GitHub Action downloads the sources and validates the complete edition. The homepage reads the arrival years, count and retrieval date from [status metadata](https://coolcode.ca/campcalendar/data/status.json). The date records when the upstream data was read. Each archive retains its original coverage. When a refresh fails the previously published edition remains available.

## Development

The browser interface lives in `web/`. Run `python3 scripts/refresh.py` to retrieve the source records. Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests`, and `python3 scripts/build.py` for a local build. Successful main builds deploy independently to GitHub Pages. Searches and comparisons stay in the browser.
