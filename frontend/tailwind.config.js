/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // XFactor Bot color scheme - matching logo
        background: "hsl(200, 25%, 18%)",      // Dark slate blue-gray (#2D3E4A)
        foreground: "hsl(38, 30%, 85%)",       // Warm cream text
        card: "hsl(200, 25%, 22%)",            // Slightly lighter slate
        "card-foreground": "hsl(38, 30%, 90%)",
        primary: "hsl(95, 35%, 45%)",          // Money green from logo
        "primary-foreground": "hsl(0, 0%, 100%)",
        secondary: "hsl(200, 20%, 28%)",       // Muted slate
        "secondary-foreground": "hsl(38, 30%, 85%)",
        muted: "hsl(200, 20%, 25%)",
        "muted-foreground": "hsl(200, 15%, 55%)",
        accent: "hsl(185, 45%, 45%)",          // Teal accent (BOT text color)
        "accent-foreground": "hsl(38, 30%, 90%)",
        destructive: "hsl(0, 70%, 55%)",
        "destructive-foreground": "hsl(0, 0%, 100%)",
        border: "hsl(200, 20%, 30%)",
        input: "hsl(200, 20%, 25%)",
        ring: "hsl(185, 45%, 45%)",
        profit: "hsl(95, 40%, 50%)",           // Green for profits
        loss: "hsl(0, 70%, 55%)",              // Red for losses
        xfactor: {
          slate: "hsl(200, 25%, 18%)",         // Main background
          robot: "hsl(200, 20%, 55%)",         // Robot metallic color
          gold: "hsl(38, 35%, 70%)",           // XFACTOR text color
          teal: "hsl(185, 45%, 45%)",          // BOT text color
          money: "hsl(95, 35%, 45%)",          // Money green
        }
      },
      fontFamily: {
        sans: ["JetBrains Mono", "monospace"],
        display: ["Impact", "Haettenschweiler", "sans-serif"],
      },
    },
  },
  plugins: [],
}
