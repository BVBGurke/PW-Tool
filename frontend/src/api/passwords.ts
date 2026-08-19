/** CSPRNG-Generierungsendpunkt. */

import { request } from "./client";
import type { GenerationInput, GenerationResponse } from "../types/api";

export const passwordApi = {
  generate: (input: GenerationInput) => request<GenerationResponse>("/passwords/generate", { method: "POST", body: input }),
};
