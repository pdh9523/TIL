package cache_sync

import (
	"context"
	"encoding/json"
	"log"
)

type Message struct {
	SenderID string `json:"sender_id"`
	Key      string `json:"key"`
}

func (c *Cache) startSubscriber(ctx context.Context) {
	ch := c.pubSub.Channel()

	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-ch:
			var cacheMsg Message
			if err := json.Unmarshal([]byte(msg.Payload), &cacheMsg); err != nil {
				log.Printf("Error unmarshalling cache message: %s", err)
				continue
			}

			if cacheMsg.SenderID == c.id {
				continue
			}

			c.local.Del(cacheMsg.Key)
		}
	}
}
