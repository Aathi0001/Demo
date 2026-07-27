import { WorkLogModel } from "./worklog";

export interface WorkLogListResponse {

    week_start: string;

    week_end: string;

    total_entries: number;

    total_duration: string;

    results: WorkLogModel[];

}
