/*
 * NTUModmap
 * modschedule
 * Module Class Schedule Unit Tests
 */

import { describe, expect, test } from "@jest/globals";
import { fetchModule, parseTeachingWeeks } from "./module";
import { readFileSync } from "fs";
import { join } from "path";
import { range } from "./util";

describe("parseTeachingWeeks()", () => {
  test("parses ''", () => {
    expect(parseTeachingWeeks("")).toStrictEqual(range(1, 15));
  });
  test("parses 'Teaching Wk2-8'", () => {
    expect(parseTeachingWeeks("Teaching Wk2-8")).toStrictEqual([
      2, 3, 4, 5, 6, 7, 8,
    ]);
  });
  test("parses 'Teaching Wk2,5-8,13'", () => {
    expect(parseTeachingWeeks("Teaching Wk2,5-8,13")).toStrictEqual([
      2, 5, 6, 7, 8, 13,
    ]);
  });
});
describe("fetchModule()", () => {
  test("fetches module information for SC2002", async () => {
    const actual = await fetchModule(2024, 1, "SC2002");
    expect(actual).toStrictEqual(
      JSON.parse(
        readFileSync(join(__dirname, "resources", "SC2002.json")).toString(),
      ),
    );
  });
});
