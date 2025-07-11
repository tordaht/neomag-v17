/**
 * Creates a numeric hash from a string.
 * @param {string} str The input string.
 * @returns {number} A numeric hash.
 */
export function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = (hash << 5) - hash + char;
        hash |= 0; // Convert to 32bit integer
    }
    return Math.abs(hash);
}

/**
 * Generates a pseudo-random number from a seed.
 * @param {number} seed The seed.
 * @returns {number} A pseudo-random number between 0 and 1.
 */
export function seededRandom(seed) {
    let x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
}

/**
 * Clamps a number between a minimum and maximum value.
 * @param {number} value The number to clamp.
 * @param {number} min The minimum value.
 * @param {number} max The maximum value.
 * @returns {number} The clamped number.
 */
export function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
} 