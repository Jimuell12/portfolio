/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        'montserrat': ['Montserrat'],
        'lato': ['Lato'],
        'garamond': ['Garamond']
    },
    animation: {
      typing: 'typing 2s steps(6), blink 1s infinite',
    },
    keyframes: {
      typing: {
        from: {
          width: '0'
        },
        to: {
          width: '6ch'
        },
      },
      blink: {
        from: {
          'border-right-color': 'transparent'
        },
        to: {
          'border-right-color': 'black'
        },
      },
    },
    },
  },
  plugins: [],
}

