# almabtrieb

- [Documentation](https://bovine.codeberg.page/almabtrieb/)
- [Repository](https://codeberg.org/bovine/almabtrieb/)

This is a client library for the [CattleDrive](https://helge.codeberg.page/cattle_grid/cattle_drive/) protocol as used by cattle_grid.
This protocol is still somewhat in development.

This library enables one to create applications using cattle_grid as a middle ware to connect to the Fediverse. Examples:

- [cattle_grid_rss](https://codeberg.org/helge/cattle_grid_rss), see also the deployed version at [rss.bovine.social](https://rss.bovine.social).
- [roboherd](https://codeberg.org/helge/roboherd)

## Supported protocols

Currently, supported are connection strings starting with `amqp`, `amqps`, `mqtt`, `mqtts`, `ws`, and `wss`.

- [MQTT 5](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html)
- [AMQP](https://www.amqp.org), I think 0.9.1 as supported by RabbitMQ

Authentication is relegated to the underlying protocol.

## Development

Run tests with

```bash
uv run pytest
```

This will lead to a lot of skipped tests. By running

```bash
uv sync --all-extras
```

you can install the amqp and mqtt libraries and thus run more tests. For the tests against an actual connection, see the next subsection.

### Running tests against a running cattle_grid instance

Create an account on cattle_grid with

```bash
python -mcattle_grid account new almabtrieb password --admin
```

Then with cattle grid running one can run

```bash
CONNECTION_STRING=mqtt://almabtrieb:password@localhost:11883 \
    uv run pytest almabtrieb/test_real.py
CONNECTION_STRING=ws://almabtrieb:password@localhost:15675/ws \
    uv run pytest almabtrieb/test_real.py
CONNECTION_STRING="amqp://almabtrieb:password@localhost:5672/" \
    uv run pytest almabtrieb/test_real.py
```
