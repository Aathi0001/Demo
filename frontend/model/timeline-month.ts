import { TimelineWeekModel } from "./timeline-week";

export interface TimelineMonthModel{

    month:number;

    month_name:string;

    total_logs:number;

    weeks:TimelineWeekModel[];

}
