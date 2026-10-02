import * as React from "react"
import { useTranslation } from "react-i18next"

import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

import {
  CalendarCheckIcon,
  CalendarDaysIcon,
  CircleHelpIcon,
  CommandIcon,
  LayoutDashboardIcon,
  PackageIcon,
  ReceiptTextIcon,
  ScissorsIcon,
  SearchIcon,
  Settings2Icon,
  UserRoundIcon,
  UsersIcon,
} from "lucide-react"

export function AppSidebar({
  ...props
}: React.ComponentProps<typeof Sidebar>) {
  const { t } = useTranslation()

  const navMain = [
    {
      title: t("navigation.dashboard"),
      url: "/admin",
      icon: <LayoutDashboardIcon />,
    },
    {
      title: t("navigation.calendar"),
      url: "/admin/agenda",
      icon: <CalendarDaysIcon />,
    },
    {
      title: t("navigation.appointments"),
      url: "#",
      icon: <CalendarCheckIcon />,
    },
    {
      title: t("navigation.clients"),
      url: "#",
      icon: <UsersIcon />,
    },
    {
      title: t("navigation.services"),
      url: "#",
      icon: <ScissorsIcon />,
    },
    {
      title: t("navigation.team"),
      url: "#",
      icon: <UserRoundIcon />,
    },
    {
      title: t("navigation.billing"),
      url: "#",
      icon: <ReceiptTextIcon />,
    },
    {
      title: t("navigation.stock"),
      url: "#",
      icon: <PackageIcon />,
    },
  ]

  const navSecondary = [
    {
      title: t("navigation.settings"),
      url: "#",
      icon: <Settings2Icon />,
    },
    {
      title: t("navigation.help"),
      url: "#",
      icon: <CircleHelpIcon />,
    },
    {
      title: t("navigation.search"),
      url: "#",
      icon: <SearchIcon />,
    },
  ]

  const user = {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  }

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              className="data-[slot=sidebar-menu-button]:p-1.5!"
              render={<a href="#" />}
            >
              <CommandIcon className="size-5!" />
              <span className="text-base font-semibold">
                Booking App
              </span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <NavMain items={navMain} />
        <NavSecondary
          items={navSecondary}
          className="mt-auto"
        />
      </SidebarContent>

      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
    </Sidebar>
  )
}