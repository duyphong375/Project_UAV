import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface PanelProps {
  title?: string
  icon?: React.ReactNode
  headerRight?: React.ReactNode
  children: React.ReactNode
  className?: string
  contentClassName?: string
  noPadding?: boolean
  scrollable?: boolean
}

export const Panel: React.FC<PanelProps> = ({
  title,
  icon,
  headerRight,
  children,
  className = '',
  contentClassName = '',
  noPadding = false,
  scrollable = false,
}) => {
  return (
    <Card className={`flex flex-col h-full overflow-hidden border-border bg-card shadow-sm ${className}`}>
      {(title || headerRight) && (
        <CardHeader className="py-2.5 px-3.5 border-b border-border/60 bg-muted/20 flex flex-row items-center justify-between space-y-0 shrink-0">
          <div className="flex items-center gap-2">
            {icon && <span className="text-muted-foreground">{icon}</span>}
            {title && (
              <CardTitle className="text-xs sm:text-sm font-semibold tracking-wide text-foreground">
                {title}
              </CardTitle>
            )}
          </div>
          {headerRight && <div className="flex items-center gap-1.5">{headerRight}</div>}
        </CardHeader>
      )}
      <CardContent
        className={`flex-1 min-h-0 min-w-0 ${scrollable ? 'overflow-auto' : 'overflow-hidden'} ${
          noPadding ? 'p-0' : 'p-3'
        } ${contentClassName}`}
      >
        {children}
      </CardContent>
    </Card>
  )
}
