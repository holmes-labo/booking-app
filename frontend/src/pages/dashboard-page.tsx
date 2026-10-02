import { SectionCards } from '@/components/section-cards'

export function DashboardPage() {
  return (
    <main className="flex flex-1 flex-col gap-4 p-4 md:p-6">
      <h1 className="text-2xl font-semibold">
        Tableau de bord
      </h1>

      <p className="text-muted-foreground">
        Votre activité en un coup d'œil.
      </p>

      <SectionCards />
    </main>
  )
}