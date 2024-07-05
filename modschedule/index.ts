#!/usr/bin/env node
/*
 * NTUModmap
 * modschedule
 */

import { program } from "@commander-js/extra-typings";
import { fetchModule } from "./module";
import { parseBlock } from "./block";
import { searchTimetable } from "./search";

// parse program options
program
  .command("modschedule")
  .description("Automatically finds random clash-free timetable given module selections.")
  .option(
    "-y, --year <year>",
    "Academic year to retrieve module indexes for.",
    new Date().getFullYear().toString(),
  )
  .option(
    "-s, --semester <semester>",
    "Academic semester to retrieve module indexes for.",
    "1",
  )
  .option(
    "-b, --block <block_csv>",
    `Blocks time interval listed in outlined in 'block_csv' from module module scheduling.
      CSV format should contain the following columns:
      - 'begin': Begin of the time interval to block in 'HHMM' format.
      - 'end': End of the time interval to block in 'HHMM' format (exclusive).
      - 'duration' Optional. If specified only 'duration' seconds would be blocked
          between 'begin' and 'end'. Must be shorter than the time interval
          delimited by 'begin' and 'end'.
      - 'weekday' Optional. If specified blocking would occur on the weekday
          specified by 3 letter short form eg. 'MON' for Monday.
      - 'teachingWeek' Optional. If specified blocked on a specific teaching week
          no. instead of on all teaching weeks.`,
  )
  .argument(
    "<module codes...>",
    "Codes specifying modules to schedule in timetable",
  )
  .action(async (modCodes, options) => {
    // fetch module information for specified modules
    const modules = await Promise.all(
      modCodes.map((code) =>
        fetchModule(
          parseInt(options["year"]),
          parseInt(options["semester"]),
          code,
        ),
      ),
    );

    // parse time blocks if specified
    const blocks = options["block"] != null ? parseBlock(options["block"]) : [];
    // search for timetable that satisfies requirements
    const timetable = searchTimetable(modules, blocks);
    if (timetable == null) {
      console.error("No timetable found");
      process.exit(1);
    }
    console.log("Found timetable:");
    console.log(JSON.stringify(timetable, null, 2));
  })
  .parse();
