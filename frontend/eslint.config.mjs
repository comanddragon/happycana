import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
    ...nextVitals,
    ...nextTs,
    {
        rules: {
            "@typescript-eslint/no-unused-vars": [
                "warn",
                { argsIgnorePattern: "^_", varsIgnorePattern: "^_", destructuredArrayIgnorePattern: "^_" },
            ],
        },
    },
    {
        // AgeGate reads localStorage in a one-time post-mount effect to avoid
        // a hydration mismatch (localStorage isn't available during SSR, so
        // the value can't be computed during render). This is the standard,
        // unavoidable exception to react-hooks/set-state-in-effect.
        files: ["src/components/home/AgeGate.tsx"],
        rules: {
            "react-hooks/set-state-in-effect": "off",
        },
    },
    globalIgnores([
        ".next/**",
        "out/**",
        "build/**",
        "next-env.d.ts",
    ]),
]);

export default eslintConfig;