# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.3.5](https://github.com/globus-gladier/gladier/compare/v0.3.4...v0.3.5) (2021-07-14)


### Features

* Added config migration system to Gladier ([cdc7875](https://github.com/globus-gladier/gladier/commit/cdc7875c1c263bcf5eb9c5c61db58ce1df75ec23))

### [0.3.4](https://github.com/globus-gladier/gladier/compare/v0.3.3...v0.3.4) (2021-07-09)


### Bug Fixes

* gladier improperly falling back onto FuncX authorizers ([3976a3a](https://github.com/globus-gladier/gladier/commit/3976a3afad2cfd9752e2828037f46b2988b47541))

### [0.3.3](https://github.com/globus-gladier/gladier/compare/v0.3.2...v0.3.3) (2021-06-18)


### Bug Fixes

* Tools with more than two states would raise error with flow gen ([dd6586e](https://github.com/globus-gladier/gladier/commit/dd6586ee9f14c9e09e4a61f08eecdb94d89b28bc))
* when user adds new AP to flow, Gladier now handles re-auth ([e24a372](https://github.com/globus-gladier/gladier/commit/e24a372ca4af71affe5d891e6a83c99eb71c933b))

### [0.3.2](https://github.com/globus-gladier/gladier/compare/v0.3.1...v0.3.2) (2021-06-17)


### Bug Fixes

* add funcx-endpoint==0.0.3 to Gladier requirements ([8ac47b8](https://github.com/globus-gladier/gladier/commit/8ac47b81a54839cd182a090219d6cdbb16079c44))

### [0.3.1](https://github.com/globus-gladier/gladier/compare/v0.3.0...v0.3.1) (2021-06-04)


### Bug Fixes

* Fixed bug when instantiating two Gladier Clients ([3aca2fe](https://github.com/globus-gladier/gladier/commit/3aca2fe6d48788bfe3a199ebe76b0a9817bc08d3))

### [0.3.0](https://github.com/globus-gladier/gladier/compare/v0.2.0...v0.3.0) (2021-05-28)


### Features

* Support flow modifiers, payload dict modifiers ([a05b77a](https://github.com/globus-gladier/gladier/commit/a05b77aa42531e80be2bdae156f060de2a4e5e20))
* FuncX ids and Flow ids are now saved in ~/.gladier-secrets.cfg instead of ./gladier.cfg
* Added support for setting Groups
* Added support for setting subscription ids

### Bug Fixes

* Added changes lost from previous merges to fix client ([c707d32](https://github.com/globus-gladier/gladier/commit/c707d321e0893d17c953d1f6fe3b6f846d298bc0))

### 0.2.0 - May 17, 2021

- Changed name ``gladier.defaults.GladierDefaults`` to ``gladier.base.GladierBaseTool``
- Changed name ``gladier.client.GladierClient`` to ``gladier.client.GladierBaseClient``

- Added a lot more documentation to the read-the-docs page!

### 0.0.1 - Apr 5, 2021

- Initial Release!