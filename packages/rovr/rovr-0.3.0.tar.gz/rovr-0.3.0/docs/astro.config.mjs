// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import sitemap from "@astrojs/sitemap";
import { viewTransitions } from "astro-vtbot/starlight-view-transitions";
import starlightLlmsTxt from "starlight-llms-txt";
import mermaid from "astro-mermaid";

export default defineConfig({
  site: "https://nspc911.github.io",
  base: "/rovr",
  integrations: [
    mermaid({}),
    starlight({
      title: "rovr",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/NSPC911/rovr",
        },
        {
          icon: "discord",
          label: "Discord",
          href: "https://nspc911.github.io/discord",
        },
      ],
      head: [
        {
          tag: 'meta',
          attrs: { property: 'og:image', content: "https://github.com/NSPC911/rovr/blob/master/img/0.1.0/rovr_thumb.png?raw=true" },
        },
        {
          tag: 'meta',
          attrs: { property: 'twitter:image', content: "https://github.com/NSPC911/rovr/blob/master/img/0.1.0/rovr_thumb.png?raw=true" },
        },
      ],
      customCss: ["./src/styles/custom.css"],
      editLink: {
        baseUrl:
          "https://github.com/NSPC911/rovr/tree/docs/docs",
      },
      tableOfContents: { minHeadingLevel: 1, maxHeadingLevel: 4 },
      lastUpdated: true,
      sidebar: [
        { label: "overview", slug: "overview" },
        {
          label: "get started",
          items: [
            { label: "installation", slug: "get-started/installation" },
            { label: "tutorial", slug: "get-started/tutorial" },
          ],
        },
        {
          label: "guides",
          items: [
            { label: "user interface", slug: "guides/user-interface" },
            { label: "file operations", slug: "guides/file-operations" },
          ],
        },
        {
          label: "configuration",
          items: [
            { label: "configuration", slug: "configuration/configuration" },
            { label: "themeing", slug: "configuration/themeing" },
          ],
        },
        {
          label: "features",
          items: [
            { label: "previewing files", slug: "features/previewing-files" },
            { label: "image previews", slug: "features/image-previews" },
            { label: "cd on quit", slug: "features/cd-on-quit" },
            { label: "search", slug: "features/search" },
            { label: "plugins", slug: "features/plugins" },
          ],
        },
        {
          label: "contributing",
          items: [
            {
              label: "how to contribute",
              slug: "contributing/how-to-contribute",
            },
            {
              label: "project structure",
              slug: "contributing/project-structure",
            },
            {
              label: "optimisations",
              slug: "contributing/optimisation",
            },
          ],
        },
        {
          label: "reference",
          items: [
            { label: "keybindings", slug: "reference/keybindings" },
            { label: "config schema", slug: "reference/schema" },
          ],
        },
      ],
      plugins: [
        viewTransitions(),
        starlightLlmsTxt({
          projectName: "rovr",
        }),
      ],
    }),
    sitemap(),
  ],
});
