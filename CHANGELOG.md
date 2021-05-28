# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

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