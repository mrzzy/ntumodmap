/*
 * NTUModmap
 * modschedule
 * Timetable Search
 */

import { FitError, Intervals, explodeBlock, explodeClass } from "./interval";
import { Block, Interval, Module, Timetable } from "./models";
import { shuffle } from "./util";

type IndexOptions = { [index: string]: Interval[][] };

function search(
  modOptions: [Module, IndexOptions][],
  blockOptions: Interval[][],
  timetable: Timetable = {},
  allocated: Intervals = new Intervals(),
  stop: { value: boolean } = { value: false },
): Timetable | null {
  if (stop.value) {
    return null;
  }
  if (modOptions.length <= 0) {
    // base case: allocated all modules
    // check allocated intervals also satisfy time blocking
    try {
      allocated.canFit(blockOptions);
    } catch (e) {
      if (e instanceof FitError) {
        return null;
      }
    }
    // signal to all recursive calls to stop
    stop.value = true;
    return timetable;
  }

  const [module, indexOptions] = modOptions.pop()!;
  for (let [index, options] of Object.entries(indexOptions)) {
    // pick 1 index for module and check if it fits with already allocated
    try {
      const intervals = allocated.canFit(options);
      allocated.fit(intervals);

      // fits: allocate module index in timetable
      timetable[module.code] = index;

      // recursively explore indexes for other modules
      const result = search(modOptions, blockOptions, timetable, allocated);
      if (result != null) {
        // found timetable!
        return result;
      }

      // revert state to backtrack index pick
      delete timetable[module.code];
      intervals.map((interval) => allocated.remove(interval));
    } catch (e) {
      if (e instanceof FitError) {
        // try another index
        continue;
      }
      throw e;
    }
  }
  // revert module for backtracking
  modOptions.push([module, indexOptions]);
  return null;
}

/**
 * Search a timetable that includes modules while respecting time blocks.
 * @param modules List of modules that should be included in the timetable.
 * @param blocks List of time blocks that should be avoided when scheduling.
 * @param [seed=null] Random seed to pass to random number generator.
 * @returns List of valid timetables: mappings of module codes to index codes.
 */
export function searchTimetable(
  modules: Module[],
  blocks: Block[],
  seed: number | null = null,
): any {
  // cache of time blocking interval options
  const blockOptions = blocks.flatMap(explodeBlock);
  // cache of module index interval options
  const modOptions =
    // shuffle module & module indexes to generate different timetables
    shuffle(modules, seed)
      .map((module) => {
        const indexes = shuffle(module.indexes, seed);
        return [
          module,
          indexes.reduce((indexOptions, index) => {
            indexOptions[index.index] = index.classes.flatMap(explodeClass);
            return indexOptions;
          }, {} as IndexOptions),
        ];
      }) as [Module, IndexOptions][];

  // track already allocated time ranges
  return search(modOptions, blockOptions);
}
