# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [0.9.0b1](https://github.com/globus-gladier/gladier/compare/v0.8.4...v0.9.0b1) (2023-07-10)


### ⚠ BREAKING CHANGES

The breaking changes below mainly affect custom Gladier Tools. See the [Migration Guide](https://gladier.readthedocs.io/en/latest/migration.html) for details. 

* ``Gladier Base Tool "funcx_functions" changed to "compute_functions"``
    * Old tools will still be backwards compatible, but will use newer function names instead
    * Tools should be migrated to use compute_functions instead of funcx_functions
* ``Input Functions previously "{name}_funcx_id" are now "{name}_function_id"
* ``Default "funcx_endpoint_compute" name changed to "compute_endpoint"
    * Naming convention "funcx_endpoint_non_compute" has been dropped and is no longer used,
    * however users are still free to name endpoints as they wish
* Default action URL is now ``https://compute.actions.globus.org``
* Task output format changed, previously ``$.MyTask.details.result[0]`` is now ``$.MyTask.details.results[0].output``
    * Both styles are currently outputted for backwards compatibility. New tooling should switch to the newer style.
* Raise exception for legacy funcx function modifiers pre-v0.9.0
* Detect and auto-update old funcx functions
* Changed funcx_endpoint_compute to compute_endpoint

### Features

* Add auto migration for older configs ([d51b95e](https://github.com/globus-gladier/gladier/commit/d51b95e112e1a62d1dd05f499f89272e040efe0f))
* Add better support for flow schemas. ([b3ab831](https://github.com/globus-gladier/gladier/commit/b3ab831adfc860e1a5c5fe8b90234f0545b8cabf))
* Add built-in support for confidential clients ([cdeb6c6](https://github.com/globus-gladier/gladier/commit/cdeb6c68fac601c2639033a1ebbbebd757c232ce))
* Relpace funcx with the new globus compute sdk package ([6257742](https://github.com/globus-gladier/gladier/commit/62577423b5a5fa4e98860a8fe22919c621199702))
* Switch to production Action Provider ([8e40235](https://github.com/globus-gladier/gladier/commit/8e40235c2b3dee0750b5057c223b12a56da2c8b4))


### Bug Fixes

* Custom Client IDs on Gladier Client classes not using correct storage ([05bbb01](https://github.com/globus-gladier/gladier/commit/05bbb01d35b0ac7cd52ae23065dfce1b0685f2b2))
* Legacy funcx functions not being registered or tracked ([1e823a7](https://github.com/globus-gladier/gladier/commit/1e823a77ecb0b4c78526c130e8157b58581cdc69))
* Raise exception for legacy funcx function modifiers pre-v0.9.0 ([739cfd3](https://github.com/globus-gladier/gladier/commit/739cfd3efaa9d16e7d57a44133d61a5621df6dfa))


* Changed funcx_endpoint_compute to compute_endpoint ([d981741](https://github.com/globus-gladier/gladier/commit/d981741dc102097e3ee5d9e09320baa8eb3052f2))
* Detect and auto-update old funcx functions ([94567fd](https://github.com/globus-gladier/gladier/commit/94567fd1367491599cc9af868d4544b9023b6bb4))


### [0.8.4](https://github.com/globus-gladier/gladier/compare/v0.8.3...v0.8.4) (2023-04-19)


### Features

* Add support for python 3.11 ([810b973](https://github.com/globus-gladier/gladier/commit/810b97343d5f8bdb105e8d52c6e6634953b1f0c6))
* Upgrade to new Globus Compute Action Provider ([4d08df5](https://github.com/globus-gladier/gladier/commit/4d08df5353eb70d3f1fc479122459400927883e3))


### [0.8.3](https://github.com/globus-gladier/gladier/compare/v0.8.2...v0.8.3) (2023-04-04)


### Bug Fixes

* State modifiers being given incorrect values for some items ([c423614](https://github.com/globus-gladier/gladier/commit/c42361470e9a11a6e4cbdaa5524212237d2d0bcd))

### [0.8.2](https://github.com/globus-gladier/gladier/compare/v0.8.1...v0.8.2) (2023-02-09)


### Bug Fixes

* CallbackLoginManager not being a top-level import ([d5a28d5](https://github.com/globus-gladier/gladier/commit/d5a28d552432b905ee29631c429def0152ec9b22))
* erroneously removed `get_flow_id()` method on Gladier Clients ([ea2232b](https://github.com/globus-gladier/gladier/commit/ea2232b7ebe731bfe7312ec9d68de02ec78ed04e))
* flow generation bug when using multiple funcx functions on a tool ([dde6389](https://github.com/globus-gladier/gladier/commit/dde638987d43483cdf657789c26ae866a0e40c26))
* Unexpected flow generation when duplicate funcx functions used ([49c07d0](https://github.com/globus-gladier/gladier/commit/49c07d02fa93acf2a7aa16e690d80a6ece6b4248))

### [0.8.1](https://github.com/globus-gladier/gladier/compare/v0.8.0...v0.8.1) (2023-01-30)


### Bug Fixes

* Add missing client ``login`` method ([74bdfa4](https://github.com/globus-gladier/gladier/commit/74bdfa4279b48e7433fcc029042a57b1bae3502f))
* Deprecate subscription_id on Gladier Clients and flows ([e75ab38](https://github.com/globus-gladier/gladier/commit/e75ab38248242395f0ff5cf613d834c95f763350))
* Multiple instantiations of a Gladier Client raising errors ([2dfd747](https://github.com/globus-gladier/gladier/commit/2dfd74771a6b44e055bd160df1309c10c34390bd))

## [0.8.0](https://github.com/globus-gladier/gladier/compare/v0.7.1...v0.8.0) (2023-01-05)


### ⚠ BREAKING CHANGES

* Requires a new login after upgrading
* Passing Authorizers to Gladier Clients has been deprecated in favor of using the new Login Manager system
* Passing `auto_login` is deprecated and will be removed
    * Disabling automatic login can be replicated by using a login manager with `CallbackLoginManager(..., callback=None)`. See [Cusomizing Auth](https://gladier.readthedocs.io/en/latest/gladier/custom_auth.html#customizing-auth) for more details.
* Gladier "public" configs have been removed
    * public configs were undocumented and shouldn't affect any normal Gladier users

### Features

* Add "flow_transition_states" to BaseTools for determining Choice state ([7053e75](https://github.com/globus-gladier/gladier/commit/7053e751d931ab933e4e5983a0a42290eeb6cbd0))
* Add login customization for use within larger apps ([39c0a0c](https://github.com/globus-gladier/gladier/commit/39c0a0ceea9e471ee35042ca2534bedc2c0b5c42))
* Add support for python 3.10 ([eaf3fec](https://github.com/globus-gladier/gladier/commit/eaf3fecaac218eda87fcd4dc24f04e3adc5e2008))
* Allow passing custom flow managers to Gladier Clients ([a2fdead](https://github.com/globus-gladier/gladier/commit/a2fdeadbe8e81e95d62d3b5365f8fd3268b0930a))
* Make the flows manager available for public usage ([b905e7c](https://github.com/globus-gladier/gladier/commit/b905e7c3f1eca559d4a2c8cb62f545c01bdf7c19))


* Login Manager and config overhauls ([6016abc](https://github.com/globus-gladier/gladier/commit/6016abc44093ba3e0901a33b5cf38e4871317a2b))
* Update Client ID from an older version ([8b4393c](https://github.com/globus-gladier/gladier/commit/8b4393c3f78766729c82e52c4bd1e7ed2c9bd8ad))

## [0.8.0b2](https://github.com/globus-gladier/gladier/compare/v0.8.0b1...v0.8.0b2) (2022-11-08)


### Features

* Add login customization for use within larger apps ([39c0a0c](https://github.com/globus-gladier/gladier/commit/39c0a0ceea9e471ee35042ca2534bedc2c0b5c42))
* Allow passing custom flow managers to Gladier Clients ([a2fdead](https://github.com/globus-gladier/gladier/commit/a2fdeadbe8e81e95d62d3b5365f8fd3268b0930a))
* Make the flows manager available for public usage ([b905e7c](https://github.com/globus-gladier/gladier/commit/b905e7c3f1eca559d4a2c8cb62f545c01bdf7c19))


## [0.8.0b1](https://github.com/globus-gladier/gladier/compare/v0.7.1...v0.8.0b1) (2022-10-26)


### ⚠ BREAKING CHANGES

* Requires a new login after upgrading.
* Gladier "public" configs have been removed.

### Features

* Support for writing tools using Flow Choice states.
* Add "flow_transition_states" to BaseTools for determining Choice state ([7053e75](https://github.com/globus-gladier/gladier/commit/7053e751d931ab933e4e5983a0a42290eeb6cbd0))
* Add support for python 3.10 ([eaf3fec](https://github.com/globus-gladier/gladier/commit/eaf3fecaac218eda87fcd4dc24f04e3adc5e2008))


* Login Manager and config overhauls ([6016abc](https://github.com/globus-gladier/gladier/commit/6016abc44093ba3e0901a33b5cf38e4871317a2b))
* Update Client ID from an older version ([8b4393c](https://github.com/globus-gladier/gladier/commit/8b4393c3f78766729c82e52c4bd1e7ed2c9bd8ad))


### [0.7.1](https://github.com/globus-gladier/gladier/compare/v0.7.0...v0.7.1) (2022-08-25)


### Bug Fixes

* Error on first time flow deployment if using group perms ([b444f2b](https://github.com/globus-gladier/gladier/commit/b444f2b8e09ab77efaa5c7d7b4f9698a1ddc9164))

## [0.7.0](https://github.com/globus-gladier/gladier/compare/v0.6.3...v0.7.0) (2022-08-22)


### ⚠ BREAKING CHANGES

* Older funcx versions before v1.0 are no longer supported.
    * No code changes are required to migrate to Gladier v0.7.0 or FuncX v1.0

### Features

* Add support for globus-automate-client 0.16 ([dc9e82c](https://github.com/globus-gladier/gladier/commit/dc9e82ca02ebf63217d9fabadada725579f038b3))
* Upgrade to funcx v1 ([c947077](https://github.com/globus-gladier/gladier/commit/c947077c733b50f3aa20d4e041dba8eb5c47da0b))


### Bug Fixes

* Aliases not working with tools that use `@generate_flow_definition` ([da30756](https://github.com/globus-gladier/gladier/commit/da3075662703298291d776b1c25fb95348a6fdaa))


### [0.6.3](https://github.com/globus-gladier/gladier/compare/v0.6.2...v0.6.3) (2022-07-20)

### Bug Fixes

* Fix error when docstring is too long ([a19a4bf](https://github.com/globus-gladier/gladier/commit/a19a4bfd7ca43a8f82ef1179071bd05c302951ef))


### [0.6.2](https://github.com/globus-gladier/gladier/compare/v0.6.1...v0.6.2) (2022-05-06)


### Bug Fixes

* Possible flows client 401 due to client caching ([3b5a307](https://github.com/globus-gladier/gladier/commit/3b5a307072e82cdc40b1292bc7225eb8b293ebe4))

### [0.6.1](https://github.com/globus-gladier/gladier/compare/v0.6.0...v0.6.1) (2022-05-05)


### Features

* Add support for globus-automate-client 0.15.x ([9ecd2e1](https://github.com/globus-gladier/gladier/commit/9ecd2e121c59795924175c8dff198c142493f477))

## [0.6.0](https://github.com/globus-gladier/gladier/compare/v0.5.4...v0.6.0) (2022-05-05)


### ⚠ BREAKING CHANGES

* The following versions of FuncX and the Globus Automate
Client will no longer be supported:

* Globus Automate Client: Requires 0.13.0 and above
* FuncX: Requires 0.3.6 and above

Older versions of these packages are only compatible with Globus SDK
v2, and require updating any code that relies on the older Globus SDK
version. See the SDK upgrade guide here:

### Features

* Added 'aliased' tool chaining feature ([48cbaaf](https://github.com/globus-gladier/gladier/commit/48cbaaf2e0e85f1ff8846ffad3ed06694a1f82b4))


### Bug Fixes

* Add packaging dependency ([95f6ec1](https://github.com/globus-gladier/gladier/commit/95f6ec1e75b72797b1aad2a90ef5f374aeef1bd5))
* Added check when adding tool without flow states ([c612383](https://github.com/globus-gladier/gladier/commit/c612383fe05ab0c7d018153b3b639df0c2b6e63f))
* Redeploy flow on 404s ([6c0d3a7](https://github.com/globus-gladier/gladier/commit/6c0d3a7cf1792ccb08cf440559b7114f7a95c03c))
* tools/flows client not properly being cached in gladier clients ([a6e5cec](https://github.com/globus-gladier/gladier/commit/a6e5cecf4928820025bb828eeb3d825a9292c5c5))


* Drop support for old versions of globus-automate-client/funcx ([5d17d96](https://github.com/globus-gladier/gladier/commit/5d17d967af16b9cd98a0ea9e3615224ad0f1c3d6)), closes [/globus-sdk-python.readthedocs.io/en/stable/upgrading.html#from-1-x-or-2-x-to-3-0](https://github.com/globus-gladier//globus-sdk-python.readthedocs.io/en/stable/upgrading.html/issues/from-1-x-or-2-x-to-3-0)

## [0.6.0b2](https://github.com/globus-gladier/gladier/compare/v0.5.4...v0.6.0b2) (2022-02-17)

### Bug Fixes

* Add packaging dependency ([95f6ec1](https://github.com/globus-gladier/gladier/commit/95f6ec1e75b72797b1aad2a90ef5f374aeef1bd5))


## [0.6.0b1](https://github.com/globus-gladier/gladier/compare/v0.5.4...v0.6.0b1) (2022-02-17)


### ⚠ BREAKING CHANGES

* The following versions of FuncX and the Globus Automate
Client will no longer be supported:

* Globus Automate Client: Requires 0.13.0 and above
* FuncX: Requires 0.3.6 and above

Older versions of these packages are only compatible with Globus SDK
v2, and require updating any code that relies on the older Globus SDK
version. See the SDK upgrade guide here:

### Features

* Added 'aliased' tool chaining feature ([48cbaaf](https://github.com/globus-gladier/gladier/commit/48cbaaf2e0e85f1ff8846ffad3ed06694a1f82b4))


### Bug Fixes

* Added check when adding tool without flow states ([c612383](https://github.com/globus-gladier/gladier/commit/c612383fe05ab0c7d018153b3b639df0c2b6e63f))
* Redeploy flow on 404s ([6c0d3a7](https://github.com/globus-gladier/gladier/commit/6c0d3a7cf1792ccb08cf440559b7114f7a95c03c))
* tools/flows client not properly being cached in gladier clients ([a6e5cec](https://github.com/globus-gladier/gladier/commit/a6e5cecf4928820025bb828eeb3d825a9292c5c5))


* Drop support for old versions of globus-automate-client/funcx ([5d17d96](https://github.com/globus-gladier/gladier/commit/5d17d967af16b9cd98a0ea9e3615224ad0f1c3d6)), closes [/globus-sdk-python.readthedocs.io/en/stable/upgrading.html#from-1-x-or-2-x-to-3-0](https://github.com/globus-gladier//globus-sdk-python.readthedocs.io/en/stable/upgrading.html/issues/from-1-x-or-2-x-to-3-0)

### [0.5.4](https://github.com/globus-gladier/gladier/compare/v0.5.3...v0.5.4) (2021-11-15)


### Bug Fixes

* Only apply migrations when needed ([670daea](https://github.com/globus-gladier/gladier/commit/670daead98ec6c4fde796ec5b5e9a60378b8da9e))

### [0.5.3](https://github.com/globus-gladier/gladier/compare/v0.5.2...v0.5.3) (2021-09-14)


### Bug Fixes

* Limits run label length to 64 chars ([53cd20f](https://github.com/globus-gladier/gladier/commit/53cd20f867c74a7f560d4008d7503b72249041ef)), closes [#146](https://github.com/globus-gladier/gladier/issues/146)

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