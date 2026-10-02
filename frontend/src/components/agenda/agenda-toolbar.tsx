import {
  ChevronLeftIcon,
  ChevronRightIcon,
} from "lucide-react"

import { Button } from "@/components/ui/button"

type AgendaToolbarProps = {
  selectedDate: Date
  onPreviousDay: () => void
  onToday: () => void
  onNextDay: () => void
}

export function AgendaToolbar({
  selectedDate,
  onPreviousDay,
  onToday,
  onNextDay,
}: AgendaToolbarProps) {
  const formattedDate = new Intl.DateTimeFormat("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(selectedDate)

  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <h2 className="text-lg font-medium capitalize">
        {formattedDate}
      </h2>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="icon"
          onClick={onPreviousDay}
          aria-label="Jour précédent"
        >
          <ChevronLeftIcon />
        </Button>

        <Button
          variant="outline"
          onClick={onToday}
        >
          Aujourd&apos;hui
        </Button>

        <Button
          variant="outline"
          size="icon"
          onClick={onNextDay}
          aria-label="Jour suivant"
        >
          <ChevronRightIcon />
        </Button>
      </div>
    </div>
  )
}