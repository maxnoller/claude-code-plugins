// counter.svelte.test.ts - Testing runes in .svelte.ts files
// File must include .svelte in its name to use runes in tests
import { describe, expect, it } from 'vitest';
import { flushSync } from 'svelte';
import { createCounter } from './counter.svelte';

describe('createCounter', () => {
    it('starts with initial value', () => {
        const counter = createCounter(5);

        // In Svelte 5, you can read $state values directly in tests
        // when the test file is named .svelte.test.ts
        expect(counter.count).toBe(5);
    });

    it('increments count', () => {
        const counter = createCounter(0);

        counter.increment();
        // flushSync forces synchronous updates for testing
        flushSync();

        expect(counter.count).toBe(1);
    });

    it('decrements count', () => {
        const counter = createCounter(10);

        counter.decrement();
        flushSync();

        expect(counter.count).toBe(9);
    });

    it('resets to initial value', () => {
        const counter = createCounter(0);

        counter.increment();
        counter.increment();
        flushSync();

        expect(counter.count).toBe(2);

        counter.reset();
        flushSync();

        expect(counter.count).toBe(0);
    });
});

// Example counter module (counter.svelte.ts):
//
// export function createCounter(initial = 0) {
//   let count = $state(initial);
//   const initialValue = initial;
//   
//   return {
//     get count() { return count },
//     increment: () => count++,
//     decrement: () => count--,
//     reset: () => count = initialValue
//   };
// }
