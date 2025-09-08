# Changelog

## 0.2.5

- Add `on_disconnect` handler [almabtrieb#24](https://codeberg.org/bovine/almabtrieb/issues/24)
- Add `python -malmabtrieb info`

## 0.2.4

- Improved connection close behavior [almabtrieb#21](https://codeberg.org/bovine/almabtrieb/issues/21)
- Add command line tool

## 0.2.3

- Remove incorrect logging potentially containing passwords

## 0.2.2 ([Milestone](https://codeberg.org/bovine/almabtrieb/milestone/10249))

- Added timeout to MQTT [almabtried#18](https://codeberg.org/bovine/almabtrieb/issues/18)
- Added timeout to AMQP connect, [almabtrieb#15](https://codeberg.org/bovine/almabtrieb/issues/15)

## 0.2.1 ([Milestone](https://codeberg.org/bovine/almabtrieb/milestone/10246))

- Add automation of release [almabtrieb#13](https://codeberg.org/bovine/almabtrieb/issues/13)
- Add name argument to create actor [almabtrieb#12](https://codeberg.org/bovine/almabtrieb/issues/12)

## 0.2.0

- Change interface, get rid of `connect` method
- Update to new Cattle Drive version

## 0.1.3

- Validate used method in trigger against the allowed methods from `method_information` in the info response.

## 0.1.2

- Set RabbitMQ queues to auto delete

## 0.1.1

- Fix [almabtrieb#7](https://codeberg.org/bovine/almabtrieb/issues/7)

## 0.1.0

Initial version
