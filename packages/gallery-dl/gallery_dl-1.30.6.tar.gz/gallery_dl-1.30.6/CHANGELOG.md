## 1.30.6 - 2025-09-06
### Extractors
#### Additions
- [chevereto] add `video` extractor ([#8149](https://github.com/mikf/gallery-dl/issues/8149))
- [comick] add `covers` extractor
- [fansly] add support ([#4401](https://github.com/mikf/gallery-dl/issues/4401))
- [instagram] add `stories-tray` extractor ([#6582](https://github.com/mikf/gallery-dl/issues/6582))
- [shimmie2] support `co.llection.pics` ([#8166](https://github.com/mikf/gallery-dl/issues/8166))
- [tungsten] add support ([#8061](https://github.com/mikf/gallery-dl/issues/8061))
- [vk] add `wall-post` extractor ([#474](https://github.com/mikf/gallery-dl/issues/474) [#6378](https://github.com/mikf/gallery-dl/issues/6378) [#8159](https://github.com/mikf/gallery-dl/issues/8159))
#### Fixes
- [bunkr] fix downloading albums with more than 100 files ([#8150](https://github.com/mikf/gallery-dl/issues/8150) [#8155](https://github.com/mikf/gallery-dl/issues/8155) [#8175](https://github.com/mikf/gallery-dl/issues/8175))
- [chevereto:user] fix names starting with an `a` ([#8149](https://github.com/mikf/gallery-dl/issues/8149))
- [common] prevent exception when using empty `user-agent` ([#8116](https://github.com/mikf/gallery-dl/issues/8116))
- [deviantart:search] fix extraction ([#8083](https://github.com/mikf/gallery-dl/issues/8083))
- [hentaifoundry:story] fix `src` & `description` extraction ([#8163](https://github.com/mikf/gallery-dl/issues/8163))
- [imagebam] update guard page bypass cookies ([#8123](https://github.com/mikf/gallery-dl/issues/8123))
- [kemono] fix `.bin` archive files not being added to archives list ([#8156](https://github.com/mikf/gallery-dl/issues/8156))
- [reddit] fix `TypeaError` when processing comments ([#8139](https://github.com/mikf/gallery-dl/issues/8139))
- [tumblr] fix pagination when using `date-max`
- [twitter] prevent exceptions in `_transform_community()` ([#8134](https://github.com/mikf/gallery-dl/issues/8134))
- [twitter] prevent `KeyError: 'name'` in `_transform_user()` ([#8154](https://github.com/mikf/gallery-dl/issues/8154))
- [twitter] fix `KeyError: 'core'` when processing communities ([#8141](https://github.com/mikf/gallery-dl/issues/8141))
- [zerochan] fix `500 Internal Server Error` during login ([#8097](https://github.com/mikf/gallery-dl/issues/8097) [#8114](https://github.com/mikf/gallery-dl/issues/8114))
#### Improvements
- [comick] detect broken chapters ([#8054](https://github.com/mikf/gallery-dl/issues/8054))
- [erome] handle reposts on user profiles ([#6582](https://github.com/mikf/gallery-dl/issues/6582))
- [instagram] improve video quality warning regex ([#8078](https://github.com/mikf/gallery-dl/issues/8078))
- [jpgfish] update domain to `jpg6.su`
- [reddit] add `api` & `limit` options ([#7997](https://github.com/mikf/gallery-dl/issues/7997) [#8012](https://github.com/mikf/gallery-dl/issues/8012) [#8092](https://github.com/mikf/gallery-dl/issues/8092))
- [reddit] support video embeds ([#8139](https://github.com/mikf/gallery-dl/issues/8139))
- [tumblr:tagged] support `/archive/tagged/` URLs ([#8160](https://github.com/mikf/gallery-dl/issues/8160))
#### Metadata
- [khinsider] extract `description` metadata
- [tumblr:tagged] provide `search_tags` metadata ([#8160](https://github.com/mikf/gallery-dl/issues/8160))
- [vk] parse `date` & `description` metadata ([#8029](https://github.com/mikf/gallery-dl/issues/8029))
- [vk:album] extract more metadata ([#8029](https://github.com/mikf/gallery-dl/issues/8029))
### Downloaders
- [ytdl] implement `_ytdl_manifest_cookies`
### Miscellaneous
- [formatter] add `R` conversion - extract URLs ([#8125](https://github.com/mikf/gallery-dl/issues/8125))
- [options] add `-a` as short option for `--user-agent`
- [scripts/init] implement `-s/--subcategory`
