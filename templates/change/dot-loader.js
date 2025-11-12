// Arrow pattern for idle state (right arrow)
// Grid 7x7: row 0-6 from left to right, then next row
// [0,1,2,3,4,5,6], [7,8,9,10,11,12,13], [14,15,16,17,18,19,20], [21,22,23,24,25,26,27], [28,29,30,31,32,33,34], [35,36,37,38,39,40,41], [42,43,44,45,46,47,48]
const ARROW_PATTERN = [10, 18, 26, 25, 24, 23, 22, 32, 38];

// DotLoader class for animating dots
class DotLoader {
    constructor(container, options = {}) {
        this.container = container;
        this.frames = options.frames || [];
        this.duration = options.duration || 150;
        this.repeatCount = options.repeatCount || -1;
        this.onComplete = options.onComplete || (() => {});
        this.isPlaying = false;
        this.currentIndex = 0;
        this.repeats = 0;
        this.interval = null;
        this.dots = [];

        this.init();
    }

    init() {
        // Create 49 dots (7x7 grid)
        this.container.innerHTML = '';
        for (let i = 0; i < 49; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot';
            this.container.appendChild(dot);
            this.dots.push(dot);
        }

        // Show arrow by default
        this.showArrow();
    }

    showArrow() {
        this.dots.forEach((dot, index) => {
            if (ARROW_PATTERN.includes(index)) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    applyFrame(frameIndex) {
        const frame = this.frames[frameIndex];
        if (!frame) return;

        this.dots.forEach((dot, index) => {
            if (frame.includes(index)) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    start() {
        if (this.isPlaying) return;

        this.isPlaying = true;
        this.currentIndex = 0;
        this.repeats = 0;

        this.interval = setInterval(() => {
            this.applyFrame(this.currentIndex);

            if (this.currentIndex + 1 >= this.frames.length) {
                if (this.repeatCount !== -1 && this.repeats + 1 >= this.repeatCount) {
                    this.stop();
                    this.onComplete();
                    return;
                }
                this.repeats++;
            }

            this.currentIndex = (this.currentIndex + 1) % this.frames.length;
        }, this.duration);
    }

    stop() {
        this.isPlaying = false;
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        // Show arrow when stopped
        this.showArrow();
    }

    reset() {
        this.stop();
        this.currentIndex = 0;
        this.repeats = 0;
    }
}

// DotFlow class for managing text transitions and dot animations
class DotFlow {
    constructor(container, items) {
        this.container = container;
        this.items = items;
        this.index = 0;
        this.textIndex = 0;
        this.dotLoaderEl = container.querySelector('.dot-loader');
        this.textEl = container.querySelector('.btn-text');
        this.dotLoader = null;

        this.init();
    }

    init() {
        // Create the dot loader with arrow
        this.dotLoader = new DotLoader(this.dotLoaderEl, {});
    }

    start() {
        if (!this.dotLoader || this.items.length === 0) return;

        this.index = 0;
        this.textIndex = 0;

        // Update text immediately without animation
        this.textEl.textContent = this.items[0].title;

        // Start first animation
        this.dotLoader.frames = this.items[0].frames;
        this.dotLoader.duration = this.items[0].duration || 150;
        this.dotLoader.repeatCount = this.items[0].repeatCount || 1;
        this.dotLoader.onComplete = () => this.next();
        this.dotLoader.start();
    }

    stop() {
        if (this.dotLoader) {
            this.dotLoader.stop();
        }
    }

    reset() {
        this.stop();
        this.index = 0;
        this.textIndex = 0;
        this.textEl.textContent = 'Run Scraper';
    }

    next() {
        this.index = (this.index + 1) % this.items.length;

        // Loop back to start, keep animating
        if (this.index === 0) {
            this.index = 0;
        }

        // Start next animation immediately without transition
        this.dotLoader.frames = this.items[this.index].frames;
        this.dotLoader.duration = this.items[this.index].duration || 150;
        this.dotLoader.repeatCount = this.items[this.index].repeatCount || 1;
        this.dotLoader.onComplete = () => this.next();
        this.dotLoader.start();
    }
}

// Animation patterns
const importing = [
    [0, 2, 4, 6, 20, 34, 48, 46, 44, 42, 28, 14, 8, 22, 36, 38, 40, 26, 12, 10, 16, 30, 24, 18, 32],
    [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47],
    [8, 22, 36, 38, 40, 26, 12, 10, 16, 30, 24, 18, 32],
    [9, 11, 15, 17, 19, 23, 25, 29, 31, 33, 37, 39],
    [16, 30, 24, 18, 32],
    [17, 23, 31, 25],
    [24],
    [17, 23, 31, 25],
    [16, 30, 24, 18, 32],
    [9, 11, 15, 17, 19, 23, 25, 29, 31, 33, 37, 39],
    [8, 22, 36, 38, 40, 26, 12, 10, 16, 30, 24, 18, 32],
    [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47],
    [0, 2, 4, 6, 20, 34, 48, 46, 44, 42, 28, 14, 8, 22, 36, 38, 40, 26, 12, 10, 16, 30, 24, 18, 32],
];

const syncing = [
    [45, 38, 31, 24, 17, 23, 25],
    [38, 31, 24, 17, 10, 16, 18],
    [31, 24, 17, 10, 3, 9, 11],
    [24, 17, 10, 3, 2, 4],
    [17, 10, 3],
    [10, 3],
    [3],
    [],
    [45],
    [45, 38, 44, 46],
    [45, 38, 31, 37, 39],
    [45, 38, 31, 24, 30, 32],
];

const searching = [
    [9, 16, 17, 15, 23],
    [10, 17, 18, 16, 24],
    [11, 18, 19, 17, 25],
    [18, 25, 26, 24, 32],
    [25, 32, 33, 31, 39],
    [32, 39, 40, 38, 46],
    [31, 38, 39, 37, 45],
    [30, 37, 38, 36, 44],
    [23, 30, 31, 29, 37],
    [31, 29, 37, 22, 24, 23, 38, 36],
    [16, 23, 24, 22, 30],
];

const heartbit = [
    [],
    [3],
    [10, 2, 4, 3],
    [17, 9, 1, 11, 5, 10, 4, 3, 2],
    [24, 16, 8, 1, 3, 5, 18, 12, 17, 11, 4, 10, 9, 2],
    [31, 23, 15, 8, 10, 2, 4, 12, 25, 19, 24, 18, 11, 17, 16, 9],
    [38, 30, 22, 15, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16],
    [38, 30, 22, 15, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16],
    [38, 30, 22, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16, 45, 37, 29, 21, 14, 8, 15, 12, 20, 27, 33, 39],
    [38, 30, 22, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16, 45, 37, 29, 21, 14, 8, 15, 12, 20, 27, 33, 39],
    [38, 30, 22, 15, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16],
    [38, 30, 22, 15, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16],
    [38, 30, 22, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16, 45, 37, 29, 21, 14, 8, 15, 12, 20, 27, 33, 39],
    [38, 30, 22, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16, 45, 37, 29, 21, 14, 8, 15, 12, 20, 27, 33, 39],
    [38, 30, 22, 15, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16],
    [38, 30, 22, 15, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16],
    [38, 30, 22, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16, 45, 37, 29, 21, 14, 8, 15, 12, 20, 27, 33, 39],
    [38, 30, 22, 17, 9, 11, 19, 32, 26, 31, 25, 18, 24, 23, 16, 45, 37, 29, 21, 14, 8, 15, 12, 20, 27, 33, 39],
    [39, 33, 37, 29, 17, 38, 30, 22, 15, 16, 23, 24, 31, 32, 25, 18, 26, 19],
    [17, 30, 16, 23, 24, 31, 32, 25, 18],
    [24],
];

const shadcn = [
    [],
    [7, 1],
    [15, 9, 7, 1],
    [23, 17, 21, 15, 9, 3],
    [31, 25, 29, 23, 17, 11],
    [39, 33, 37, 31, 25, 19],
    [47, 41, 45, 39, 33, 27],
    [47, 41, 45, 39, 33, 27],
    [47, 41, 45, 39, 33, 27],
    [47, 41, 45, 39, 33, 27],
];

// Animation frames for the scraper process
const scraperAnimationFrames = [
    {
        title: 'Running',
        duration: 100,
        repeatCount: 2,
        frames: importing
    },
    {
        title: 'Running',
        duration: 120,
        repeatCount: 2,
        frames: syncing
    },
    {
        title: 'Running',
        duration: 90,
        repeatCount: 2,
        frames: searching
    },
    {
        title: 'Running',
        duration: 80,
        repeatCount: 1,
        frames: heartbit
    },
    {
        title: 'Running',
        duration: 100,
        repeatCount: 3,
        frames: shadcn
    },
];
