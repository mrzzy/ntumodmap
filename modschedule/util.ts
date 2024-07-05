/*
 * NTUModmap
 * modschedule
 * Utilities
 */
import Rand from "rand-seed";

/** Generate & return a range of indices from begin to end (exclusive). */
export function range(begin: number, end: number): Array<number> {
  return Array(end - begin)
    .fill(begin)
    .map((x, i) => x + i);
}

/** Compute the number of seconds since the start of the day (12am). */
export function dayOffset(timestamp: Date): number {
  return (
    timestamp.getHours() * 3600 +
    timestamp.getMinutes() * 60 +
    timestamp.getSeconds()
  );
}

/**
 * Shuffle the given elements in-place using Fisher-Yates algorithm.
 * @param elements List of elements to shuffle.
 * @param [seed=null] Random seed to pass to random number generator.
 * @returns Given elements shuffled.
 */
export function shuffle<T>(elements: T[], seed: number | null = null): T[] {
  const rand = new Rand(seed?.toString());
  if (elements.length < 2) {
    return elements;
  }
  range(0, elements.length - 2).forEach((i) => {
    const j = Math.floor(rand.next() * (elements.length - 1));
    [elements[i], elements[j]] = [elements[j], elements[i]];
  });
  return elements;
}
