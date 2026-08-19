import {ProductVideo} from "@/types";
import {Play} from "lucide-react";
import {mediaUrl} from "@/lib/utils";

export function VideoPlayer({ video }: { video: ProductVideo }) {
    if (!video.playback_url) return (
        <div className="h-full w-full flex items-center justify-center bg-muted">
            <Play className="h-12 w-12 text-muted-foreground/30" />
        </div>
    )

    if (video.video_type === 'youtube') {
        const id = extractYouTubeId(video.playback_url)
        if (id) return (
            <iframe
                src={`https://www.youtube.com/embed/${id}?autoplay=0&rel=0`}
                className="h-full w-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
            />
        )
    }

    if (video.video_type === 'vimeo') {
        const id = extractVimeoId(video.playback_url)
        if (id) return (
            <iframe
                src={`https://player.vimeo.com/video/${id}`}
                className="h-full w-full"
                allow="autoplay; fullscreen; picture-in-picture"
                allowFullScreen
            />
        )
    }

    // Direct upload
    return (
        <video controls className="h-full w-full object-contain bg-black"
               poster={mediaUrl(video.thumbnail_url) ?? undefined}>
            <source src={mediaUrl(video.playback_url) ?? ''} />
        </video>
    )
}

function extractYouTubeId(url: string): string | null {
    const m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\s]+)/)
    return m?.[1] ?? null
}

function extractVimeoId(url: string): string | null {
    const m = url.match(/vimeo\.com\/(\d+)/)
    return m?.[1] ?? null
}