import type { RouteConfig } from "@react-router/dev/routes";

export default [
  {
    path: "/",
    file: "routes/_index.tsx",
    index: true,
  },
  {
    path: "/property/:id",
    file: "routes/property.$id.tsx",
  },
] satisfies RouteConfig;