/*
  Warnings:

  - You are about to drop the `FacebookImage` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Vehicle` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `_FacebookImageToVehicle` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "_FacebookImageToVehicle" DROP CONSTRAINT "_FacebookImageToVehicle_A_fkey";

-- DropForeignKey
ALTER TABLE "_FacebookImageToVehicle" DROP CONSTRAINT "_FacebookImageToVehicle_B_fkey";

-- DropTable
DROP TABLE "FacebookImage";

-- DropTable
DROP TABLE "Vehicle";

-- DropTable
DROP TABLE "_FacebookImageToVehicle";

-- CreateTable
CREATE TABLE "FacebookUser" (
    "id" TEXT NOT NULL,
    "photo" TEXT,
    "gender" TEXT,
    "first_name" TEXT,
    "last_name" TEXT,
    "name" TEXT,
    "url" TEXT,

    CONSTRAINT "FacebookUser_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "FacebookUser_id_key" ON "FacebookUser"("id");
