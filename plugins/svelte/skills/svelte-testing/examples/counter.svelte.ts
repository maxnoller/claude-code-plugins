export function createCounter(initial = 0) {
    let count = $state(initial);
    const initialValue = initial;

    return {
        get count() { return count },
        increment: () => count++,
        decrement: () => count--,
        reset: () => count = initialValue
    };
}
