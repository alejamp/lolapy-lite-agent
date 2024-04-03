
# Changelog

<!-- ## [Unreleased]

### Added
- New feature X
- New feature Y

### Changed
- Improved performance of feature A
- Updated dependency B to version 2.0

### Fixed
- Bug in feature C that caused crashes -->
## [0.4.0] - 2023-08-3

### Added
- Add local session store available in context ```ctx.session_store```. This store is a dict isolated for each user session. So you can store data in this dict and it will be available in the next message from the user. This is useful to store data that you need to use in the next message from the user. For example, if you need to ask the user for a confirmation, you can store the data that you need to confirm in the session store and then check it in the next message from the user.
Session store has two flavors of storage: In Memory or Redis. In memory is the default, but you can use Redis by passing redis_url to Lola SDK: 

```python
lola = LolaSDK(
    lola_token=token,
    redis_url="redis://localhost:6379",
    prompter_url='http://localhost:4000',
    webhook_url='http://localhost:5000')
```

Remember that you need to have Redis installed and running in your machine or in a remote server. 

- Add Stats to user Context. Stats are a dict containing a set of metric such as Tokens used, Messages sent, etc. You can access this dict in the context object ```ctx.stats```. This is useful to track the usage of your assistant, implement hard limits, etc.

## [0.3.0] - 2023-08-1

### Added
- New support for debugging. Now you can start lola SDK with ``` lola.listan(debug=True) ``` 
this will print all the debug messages that are sent and received from the server.


## [0.2.2] - 2023-07-15

### Changed
- Add easy way to set timeout with less code: 
```python 
ctx.set_timeout(5, '5_seconds_without_message')
```


## [0.2.0] - 2023-07-10

### Added
- Session Id to session object, this is the unique id for the user session
- Timeout controller and handlers: now you can set a timeout for the user to respond to a message and handle the timeout event


### Changed
- **lead** parameter for **session** parameter on functions on_event and on_command, lead is now a property of session


### Fixed
- None