<%*
  let title = tp.file.title;

  if (title.startsWith("Untitled")) {
    title = await tp.system.prompt("제목을 입력해주세요");

    if (!title || title.trim() === "") {
      const file = tp.file.find_tfile(tp.file.path(true));
      await app.vault.trash(file, false);
      return;
    }

    await tp.file.rename(title);
  }

  const slug = title
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\-]/g, '');

  const nowISO  = tp.date.now("YYYY-MM-DDTHH:mm:ssZ");
  const created = tp.date.now("YYYY-MM-DD");
  const updated = tp.file.last_modified_date("YYYY-MM-DD");

  tR += `---
title: "${title}"
date: ${nowISO}
draft: true
slug: "${slug}"
tags: []
categories: []
summary: ""
weight: 1
bookHidden: false
---
# **${title}**
`;
%>
