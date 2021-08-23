# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.5.2](https://github.com/globus-gladier/gladier/compare/v0.5.1...v0.5.2) (2021-08-23)


### Features

* Expanded flow modifiers to accept all top level state fields ([3b3135f](https://github.com/globus-gladier/gladier/commit/3b3135f3e962661c70a1aa126589f9842e466f61))


### Bug Fixes

* Flow Modifier errors not propagating Client or Tool names ([1af9724](https://github.com/globus-gladier/gladier/commit/1af972431615e0d9ff1a13354bedf35bb72a33ca))
* Remove funcx-endpoint version check ([8fe88a3](https://github.com/globus-gladier/gladier/commit/8fe88a3094a1b4fb3204c176db3318c0bc273b8b))

### [0.5.1](https://github.com/globus-gladier/gladier/compare/v0.5.0...v0.5.1) (2021-08-19)


### Bug Fixes

* Deploying new flows with the latest version of the flows service ([afa5adf](https://github.com/globus-gladier/gladier/commit/afa5adfa321971ff359a6d60b7d428294ecab477))

## [0.5.0](https://github.com/globus-gladier/gladier/compare/v0.4.1...v0.5.0) (2021-08-05)


### ⚠ BREAKING CHANGES

* Removal of older introductory testing tools

### Bug Fixes

* logout not properly clearing authorizers cache ([05b0d6c](https://github.com/globus-gladier/gladier/commit/05b0d6c7d958baf41787e282e017407c1d213cfe))
* Pass an 'empty' schema by default to fulfill automate requirement ([bf9eb80](https://github.com/globus-gladier/gladier/commit/bf9eb801446b8dc85f6dddce4101264229068861))
* pin automate version to avoid future incompatible releases ([b736fa2](https://github.com/globus-gladier/gladier/commit/b736fa20f36190b3fb5192632aeedc3a46e2ec07))
* Raise better exception when no flow definition set on tool ([eb8ac03](https://github.com/globus-gladier/gladier/commit/eb8ac03c9483b354fa65b14fa716cee2826f5928))


* Remove old "Hello World" tools. We have better ones now. ([3a889f9](https://github.com/globus-gladier/gladier/commit/3a889f98cc21dc2c5e883cb3fb4c748905629d0a))

### [0.4.1](https://github.com/globus-gladier/gladier/compare/v0.4.0...v0.4.1) (2021-07-20)

### Features

* Added get_run_url for fetching the link to a running flow in the Globus webapp
* Arguments to run_flow support pass through args to the flows service

## [0.4.0](https://github.com/globus-gladier/gladier/compare/v0.3.4...v0.4.0) (2021-07-19)


### ⚠ BREAKING CHANGES

* -- This will break all current funcx functions without
modification. Everyone will need to upgrade to the new funcX endpoint
package wherever they are executing functions. See the full migration doc
in [Migrating to V0.4.0](https://gladier.readthedocs.io/en/latest/migration.html#migrating-to-v0-4-0)

### Features

* Upgrade to FuncX 0.2.3 (from 0.0.5) ([83507f7](https://github.com/globus-gladier/gladier/commit/83507f79d0de2332a4f10e063284fc7685581f9c))

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