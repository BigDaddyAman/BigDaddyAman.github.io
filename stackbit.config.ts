import { defineStackbitConfig } from '@stackbit/types';

export default defineStackbitConfig({
    nodeVersion: '18',
    devCommand: 'npm run dev',
    buildCommand: 'npm run build',
    ...
});
