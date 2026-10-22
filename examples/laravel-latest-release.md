# Laravel Latest Release Notes (Laravel 13.x)

## Summary
The latest Laravel line is 13.x, released March 17, 2026, and the newest minor release I could find is 13.36. Its headline changes are `Rule::` builders for the remaining validation rules, `DB::olap()` for PlanetScale, and an option to reset sticky connections between queue jobs [1]. Patch releases under 13.x ship often, and the recent ones (13.31 to 13.36) add queue, Eloquent, and validation features [1][2].

## Laravel 13 at a glance
- Laravel 13 was released March 17, 2026. Bug fixes run until Q3 2027 and security fixes until March 17, 2028 [2].
- It requires PHP 8.3 or higher, and supports PHP 8.3 to 8.5 [2].
- The team focused on minimizing breaking changes, so most apps can upgrade with little code change [2].
- Major features include the first-party Laravel AI SDK, first-party JSON:API resources, `PreventRequestForgery` middleware, `Queue::route(...)`, expanded PHP attribute support, `Cache::touch(...)`, and native vector/semantic search [2].

## Recent 13.x releases
- **13.36:** `Rule::` builders for remaining validation rules, `DB::olap()` for PlanetScale, and an option to reset sticky connections between queue jobs [1].
- **13.35:** `Route::query()`, an opt-in `defaults()` method for models, property arrays in fake assertions, percentage-based worker memory limits, and more [1].
- **13.34:** Worker crashes count toward `maxExceptions`, interruptible jobs are notified before a timeout, and job durations are added to `JobProcessed` [1].
- **13.33:** Tags for `Cache::memo()`, a `Refreshes` attribute for generated columns, `AsCollection::nullable()`, and `inplace()` index migrations [1].
- **13.32:** A Mercure broadcast driver, `Storage::copyToDisk()` and `moveToDisk()`, and enum support in queue pause/resume [1].
- **13.31:** `Queue::totalSize()`, a `JobInterrupted` event, and chaperone support for `BelongsToMany` pivot models [1].
- **13.27:** Query binding masking in exception messages, `whereBinary()`, `refreshForUpdate()`, and a `Cloud` facade [1].
- **13.26:** A read-through filesystem driver, debounced queued event listeners, `Queue::forward()` routing, and process testing helpers [1].

## Notable changes from the changelog
- Typesense Scout now supports `semantic()` and `hybrid()` searches [3].
- MariaDB vector queries were fixed, and a new `AsVector` Eloquent cast was added [3].
- Laravel Echo gained a Mercure connector [3].
- Horizon supervisors can use a log-based auto-scaling strategy [3].
- `chunkBy()` was added to collections [3].

## Caveats
- I could not open the 13.36 release page directly. Its details come from the Laravel News archive summary [1].
- Patch releases are frequent, so check the GitHub releases page for the most current list [4].

## Sources
- [1] Laravel Releases: Latest Version (13.x), Changelog & Release Notes - https://laravel-news.com/tag/releases
- [2] Release Notes | Laravel 13.x - https://laravel.com/docs/releases
- [3] Changelog | Laravel 13.x - https://laravel.com/framework/docs/changelog
- [4] Releases · laravel/framework · GitHub - https://github.com/laravel/framework/releases